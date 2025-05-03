import json
import os
import time
from dotenv import load_dotenv
from flask import jsonify, request
import openai
from components.Suggestions_Component.prompt import Prompt
from database.modified_design_repository import ModifiedDesignsRepository

from utils.helpers import extract_json_from_response

class Modification:

    def __init__(self):
        load_dotenv()  
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(apikey=self.openai_key)
        prompt = Prompt("Project 2.png")
        self.modified_designs_repo = ModifiedDesignsRepository()

    NIELSEN_HEURISTICS = {
        "Visibility of system status": "The system should always keep users informed about what is going on",
        "Match between system and real world": "The system should speak the users' language",
        "User control and freedom": "Users need clearly marked 'emergency exits'",
        "Consistency and standards": "Users should not have to wonder if different words mean the same thing",
        "Error prevention": "Prevent problems from occurring in the first place",
        "Recognition rather than recall": "Minimize the user's memory load",
        "Flexibility and efficiency": "Allow users to tailor frequent actions",
        "Aesthetic and minimalist design": "Dialogues should not contain irrelevant information",
        "Help users recognize errors": "Error messages should be expressed in plain language",
        "Help and documentation": "Even though it's better if the system can be used without documentation"
    }
    
    def modify_design(self):
        
        try:
            data = request.get_json()
            print("Received design modification request")

            if not data or 'design_json' not in data:
                return jsonify({"status": "error", "message": "No design data provided"}), 400

            # Simplify the design JSON to reduce token usage
            simplified_design = {
                "metadata": data['design_json'].get('metadata', {}),
                "elements": [
                    {
                        "id": elem.get('id'),
                        "name": elem.get('name', '')[:50],
                        "type": elem.get('type'),
                        "textContent": elem.get('textContent', '')[:100],
                        "width": elem.get('width'),
                        "height": elem.get('height'),
                        "position": {
                            "x": elem.get('position.x'),
                            "y": elem.get('position.y')
                        },
                        "rotation": elem.get('rotation'),
                        "color": {
                            "r": elem.get('color_r', 0),
                            "g": elem.get('color_g', 0), 
                            "b": elem.get('color_b', 0)
                        },
                        "interactions": {
                            "hasClickInteraction": elem.get('hasClickInteraction', False),
                            "clickDestination": elem.get('clickDestination', '')[:50]
                        },
                        "isIcon": elem.get('isIcon', False),
                        "isIconLabeled": elem.get('isIconLabeled', False)
                    }
                    for elem in data['design_json'].get('elements', [])[:15]  # Limited to 15 elements
                ]
            }

            system_message = """You are a UX analyzer that returns perfect JSON with:
                - "status": "success"
                - "summary": "brief assessment"
                - "modified_design": {original JSON with fixes}
                - "modifications": [{
                    "element_id": "id",
                    "element_name": "name",
                    "type": "element type",
                    "changes": [{
                        "property": "which property",
                        "from": "original value",
                        "to": "new value",
                        "reason": "why this improves the WHOLE design",
                        "impact_analysis": "how this affects other elements"
                    }]
                }]
                Return ONLY the JSON object."""
            
            prompt = f"""Analyze and improve this design:
            {json.dumps(simplified_design, indent=2)}

            Instructions:
            1. Keep responses under 4000 tokens
            2. Return complete JSON (no truncation)
            3. Focus on key usability issues
            4. In 'modified_design', include:
            - metadata: screenWidth, screenHeight
            - elements: array of objects with:
                - id: unique identifier
                - type: element type 
                - text: text content or label
                - color: RGB string 
                - x, y: position in pixels
                - width, height: dimensions in pixels (for RECTANGLE, FRAME)
                - fontSize: font size in pixels (for TEXT)
                - fontFamily: font family 
                - interactions: optional
            5. evaluate the design according to the 10 Nielsen's UI/UX rules: {self.NIELSEN_HEURISTICS}
            6. Infer reasonable values for x, y, width, height, fontSize, fontFamily if missing (e.g., avoid overlap, align elements).
            Example:
            {{
            "metadata": {{ "screenWidth": 1440, "screenHeight": 2491 }},
            "elements": [
                {{ "id": "1:1", "type": "FRAME", "text": "Home page", "color": "rgb(255,255,255)", "width": 1440, "height": 2491 }},
                {{ "id": "1:2", "type": "RECTANGLE", "text": "Rectangle 3", "color": "rgb(0,0,0)", "x": 20, "y": 20, "width": 100, "height": 100 }},
                {{ "id": "1:3", "type": "TEXT", "text": "Rectangle 3 Label", "color": "rgb(0,0,0)", "x": 20, "y": 0, "fontSize": 12, "fontFamily": "Roboto" }}
            ]
            }}"""
            

            # Retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=4000,  # Increased token limit
                        response_format={"type": "json_object"}
                    )

                    content = response.choices[0].message.content
                    print(f"Received response length: {len(content)} characters")

                    # Check for truncation
                    if not content.strip().endswith('}'):
                        print(f"Warning: Response may be truncated on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Wait before retrying
                            continue
                        else:
                            return jsonify({
                                "status": "error",
                                "message": "Response truncated after max retries",
                                "content": content[:500] + "..." if len(content) > 500 else content
                            }), 500

                    modifications = extract_json_from_response(content)

                    # Validate response structure
                    if not all(k in modifications for k in ['status', 'summary', 'modified_design', 'modifications']):
                        raise ValueError("Missing required fields in response")

                    # Save to database
                    doc_id, files = self.modified_designs_repo.save_modification_record(
                        original_data=data,
                        modified_json=modifications
                    )

                    return jsonify({
                        "status": "success",
                        "document_id": doc_id,
                        "result": modifications,
                        "modified_design": modifications['modified_design'],
                        "modifications": modifications.get('modifications', []),
                        "summary": modifications.get('summary', 'Design analysis complete'),
                        "files": files
                    })

                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retrying
                        continue
                    return jsonify({
                        "status": "error",
                        "message": f"Failed after {max_retries} attempts: {str(e)}",
                        "content": content[:500] + "..." if 'content' in locals() and len(content) > 500 else content if 'content' in locals() else ""
                    }), 500

        except Exception as e:
            print(f"Server Error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500