import json
import os
from flask import jsonify, request
from openai import OpenAI
from database.modified_design_repository import ModifiedDesignsRepository
from utils.helpers import extract_json_from_response
from utils.ui_generator import generate_visual_ui_from_json, html_to_image

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modified_designs_repo = ModifiedDesignsRepository()

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

def modify_design():
    try:
        data = request.get_json()
        print("Received design modification request")

        if not data or 'design_json' not in data:
            return jsonify({"status": "error", "message": "No design data provided"}), 400

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
                for elem in data['design_json'].get('elements', [])[:15]
            ]
        }

        system_message = """You are an expert UX analyzer that suggests holistic design improvements. Return JSON with:
- \"status\": \"success\"
- \"summary\": \"assessment considering whole design\"
- \"modifications\": [{
    \"element_id\": \"id\",
    \"element_name\": \"name\",
    \"type\": \"element type\",
    \"changes\": [{
        \"property\": \"which property\",
        \"from\": \"original value\",
        \"to\": \"new value\",
        \"reason\": \"why this improves the WHOLE design\",
        \"impact_analysis\": \"how this affects other elements\"
    }]
}]
RULES:
1. Consider the ENTIRE design context for each change
2. Consider the 10 Nielsen's UI/UX rules: {NIELSEN_HEURISTICS}
3. Check for potential overlaps/conflicts with other elements
4. Maintain visual hierarchy and consistency
5. Maximum 3 most impactful changes per element
. Keep response under 2000 tokens"""

        prompt = f"""Analyze this design holistically:
{json.dumps(simplified_design, indent=2)}

Suggest improvements that:
1. Consider relationships between all elements
2. Maintain proper spacing and alignment
3. Preserve visual hierarchy
4. Avoid overlapping or obscuring other elements
5. Explain how each change affects the whole design"""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        print(f"Response length: {len(content)} chars")

        try:
            modifications = extract_json_from_response(content)
            valid_modifications = []
            for mod in modifications.get('modifications', []):
                if not isinstance(mod, dict) or 'element_id' not in mod:
                    continue

                clean_mod = {
                    "element_id": mod.get('element_id'),
                    "element_name": mod.get('element_name', ''),
                    "type": mod.get('type', ''),
                    "changes": [
                        {
                            "property": str(change.get('property', '')),
                            "from": str(change.get('from', '')),
                            "to": str(change.get('to', '')),
                            "reason": str(change.get('reason', ''))[:100],
                            "impact_analysis": str(change.get('impact_analysis', ''))[:150]
                        }
                        for change in mod.get('changes', [])
                        if isinstance(change, dict)
                    ][:2]
                }
                if clean_mod['changes']:
                    valid_modifications.append(clean_mod)

            doc_id, files = modified_designs_repo.save_modification_record(
                original_data=data,
                modified_json={
                    "summary": modifications.get('summary', 'Design analysis complete'),
                    "modifications": valid_modifications
                }
            )

            output_type = data.get("output_type", "json")

            if output_type == "ui_image":
                html = generate_visual_ui_from_json(valid_modifications)
                image_path = html_to_image(html)
                return jsonify({
                    "status": "success",
                    "image_url": f"/static/{os.path.basename(image_path)}"
                })

            return jsonify({
                "status": "success",
                "document_id": doc_id,
                "modifications": valid_modifications,
                "summary": modifications.get('summary', 'Design analysis complete'),
                "files": files
            })

        except Exception as e:
            print(f"Response processing error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Could not process AI response",
                "content": content[:500] + ("..." if len(content) > 500 else "")
            }), 500

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500