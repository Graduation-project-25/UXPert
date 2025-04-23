import json
import os
import pandas as pd
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import app
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from dotenv import load_dotenv
import re
from json.decoder import JSONDecodeError
import openai
from openai import OpenAI, files 
import json

from database.modified_design_repository import ModifiedDesignsRepository 


load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

figma_repository = FigmaFeaturesRepository()       
feedback_repository = FeedbackRepository()       


# Initialize Flask
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Define output folder
dataset_folder = './data/raw/EGFE'
main_output_folder = dataset_folder + '/extractedFeatures'


def clean_prefix(text):
    """Remove numeric prefixes like '0:' or '1:' from text."""
    return re.sub(r'^\d+:\s*', '', str(text))

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  
   
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    #Extract Design Information
    user_name = data.get("user_name", "Unknown User")
    design_name = data.get("design_name", "Untitled Design")
    page_name = data.get("page_name", "DefaultPage")
    frame_info = data.get("frame", {})
    frame_name = frame_info.get("frameName", "")
    elements = data.get('elements', [])
    
    if not elements:
        return jsonify({"error": "No elements found"}), 400
   
    elements_df = pd.DataFrame(elements)
  
    try:
      
        feature_data = {
            "user_name": user_name,
            "design_name": design_name,
            "page_name": page_name,
            "frame_name": frame_name,
            "screen_size": frame_info,
            "elements": elements
        }
        recognition_feedback_list = []  


        print("Attempting to insert data into MongoDB...")
        insert_result = figma_repository.update_or_insert_frame(feature_data)
    
        print("Data inserted successfully.")
        if insert_result.matched_count > 0:
            print(f"Frame added to existing design: {design_name}")
        else:
            print(f"New design document created: {design_name}")


        #Retrieve Saved Design
        latest_saved_data = figma_repository.get_saved_design(design_name, frame_name)

        if not latest_saved_data:
            print("Failed to retrieve saved design data from MongoDB")
            return jsonify({"error": "Failed to retrieve saved design data"}), 500


        # Extract elements from the retrieved design data
        frames = latest_saved_data.get("frames", [])
        if not frames:
            return jsonify({"error": "No frames found in the retrieved design"}), 500

        elements_list = [elem for frame in frames for elem in frame.get("elements", [])]

        if not elements_list:
            return jsonify({"error": "No elements found in the retrieved frames"}), 500

        elements_db = pd.DataFrame(elements_list)

        designs_for_evaluation = [{"elements": elements_db}]

        output_data = {
            "screen_size": frame_info,  
            "elements": elements,
        }

        frame_data = latest_saved_data.get("frames", [])
        if frame_data:
            elements_df = pd.DataFrame(frame_data[0].get("elements", []))
        else:
            return jsonify({"error": "No elements found in the retrieved frame data"}), 500
   
        screen_width = frame_info["screen_width"]  
        screen_height = frame_info["screen_height"]  

       
        consistency_evaluator = HeuristicFactory.check_rule("consistency")
        minimalist_evaluator = HeuristicFactory.check_rule("minimalist")
        recognition_evaluator = HeuristicFactory.check_rule("recognition")
        error_handling_evaluator = HeuristicFactory.check_rule("errorHandling")
        error_prevention_evaluator = HeuristicFactory.check_rule("errorPrevention")

        # Evaluate Rules
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)
        minimalist_results, minimalist_score = minimalist_evaluator.evaluate_rule({"elements": elements}, screen_width, screen_height)
        error_handling_results = error_handling_evaluator.evaluate_rule(elements_df)
        error_prevention_results = error_prevention_evaluator.evaluate_rule(elements_db)
        for element in elements:
            recognition_results = recognition_evaluator.evaluate_rule(element, element["type"], screen_width, screen_height, element["isIconLabeled"], element["width"], element["height"])
            if recognition_results:  
                recognition_feedback = {
                    "element_id": element["id"],
                    "element_name": element["name"],
                    "element_type": element["type"],
                    "Feedback": recognition_results,  
                }
                recognition_feedback_list.append(recognition_feedback) 

        # Transform minimalist results to match recognition structure with specific keys
        cleaned_minimalist_feedback = []
        if isinstance(minimalist_results, dict):
            # Map dictionary keys to specific labels
            for key, value in minimalist_results.items():
                cleaned_key = clean_prefix(key)
                if "white space" in cleaned_key.lower():
                    issue = "White Space Ratio"
                elif "elements" in cleaned_key.lower() and "irrelevant" not in cleaned_key.lower():
                    issue = "Number of Elements"
                elif "irrelevant" in cleaned_key.lower():
                    issue = "Irrelevant Elements"
                elif "score" in cleaned_key.lower():
                    issue = "Score"
                else:
                    issue = cleaned_key
                cleaned_minimalist_feedback.append({
                    "issue": issue,
                    "feedback": clean_prefix(value) if isinstance(value, str) else str(value)
                })
        elif isinstance(minimalist_results, list):
            # Map list items to specific labels based on content
            for i, item in enumerate(minimalist_results):
                if isinstance(item, str):
                    cleaned_item = clean_prefix(item)
                    if "white space" in cleaned_item.lower():
                        issue = "White Space Ratio"
                    elif "elements" in cleaned_item.lower() and "irrelevant" not in cleaned_item.lower():
                        issue = "Number of Elements"
                    elif "irrelevant" in cleaned_item.lower():
                        issue = "Irrelevant Elements"
                    elif "score" in cleaned_item.lower():
                        issue = "Score"
                    else:
                        issue = "Feedback"  # Fallback for unrecognized items
                    cleaned_minimalist_feedback.append({
                        "issue": issue,
                        "feedback": cleaned_item
                    })
                elif isinstance(item, dict):
                    cleaned_minimalist_feedback.append({
                        "issue": clean_prefix(item.get('issue', '')),
                        "feedback": clean_prefix(item.get('feedback', '')) if isinstance(item.get('feedback'), str) else str(item.get('feedback', ''))
                    })
        else:
            cleaned_minimalist_feedback.append({
                "issue": "Score",
                "feedback": clean_prefix(str(minimalist_results))
            })

        # Prepare human-readable feedback
        consistency_feedback = {
            "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
            "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
            "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
            # "TotalConsistency": f"Total consistency score is {consistency_results.get('TotalConsistency', 0)}%.",
            "Feedback": consistency_results.get('Feedback', {})
        }

        error_feedback = {
            "ErrorPreventionScore": f"Error Prevention Score: {error_prevention_results.get('ErrorPreventionScore', 0)}%.",
            "ValidationIssues": error_prevention_results.get("ValidationIssues", []),
            "ConfirmationIssues": error_prevention_results.get("ConfirmationIssues", []),
            "Feedback": error_prevention_results.get("Feedback", {})
        }
        
        error_handling_feedback = {
            "ErrorHandlingScore": f"Error Handling Score: {error_handling_results.get('ErrorHandlingScore', 0)}%.",
            "ErrorIssues": error_handling_results.get("ErrorIssues", []),
            "RecoveryIssues": error_handling_results.get("RecoveryIssues", []),
            "Feedback": error_handling_results
        }
        minimalist_feedback = {
            "Feedback": cleaned_minimalist_feedback,  
            # "Score": f"Final Score: {minimalist_score:.2f}%"  # Score from Minimalist
        }

        feedback_data = {
            "error_prevention_results": error_prevention_results,
            "consistency_results": consistency_results,
            "error_handling_results": error_handling_results,
            "minimalist_results": minimalist_feedback,  
        }
        if recognition_feedback_list:  # Add only if there are results
            feedback_data["recognition_results"] = recognition_feedback_list

        # Update feedback in database
        update_result = feedback_repository.update_feedback(design_name, frame_name, feedback_data)

        if update_result.matched_count == 0:
            print("Error updating feedback in MongoDB.")
            return jsonify({"error": "Failed to update feedback in database"}), 500
        print("Feedback saved successfully.")


        # Prepare final response
        response_data = {
            "message": "Design processed successfully!",
            "status": 200,
            "error_prevention_results": error_feedback,
            "consistency_results": consistency_feedback,
            "error_handling_results": error_handling_feedback,
            "minimalist_results": minimalist_feedback,
        }
        if recognition_feedback_list:  # Add only if there are results
            response_data["recognition_results"] = recognition_feedback_list

        return jsonify(response_data), 200
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


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

def extract_json_from_response(text):
    """Robust JSON extraction that handles truncated responses"""
    text = text.strip()
    
    # First try parsing directly
    try:
        return json.loads(text)
    except JSONDecodeError as e:
        pass  # We'll try other methods
        
    # Try to find complete JSON object (handles truncated responses)
    try:
        # Look for complete objects within curly braces
        json_str = re.search(r'\{.*\}', text, re.DOTALL)
        if json_str:
            # Count braces to ensure we have balanced pairs
            open_braces = json_str.group().count('{')
            close_braces = json_str.group().count('}')
            
            # If unbalanced, try to fix by adding missing braces
            if open_braces > close_braces:
                fixed_json = json_str.group() + '}' * (open_braces - close_braces)
                return json.loads(fixed_json)
            elif close_braces > open_braces:
                fixed_json = '{' * (close_braces - open_braces) + json_str.group()
                return json.loads(fixed_json)
            return json.loads(json_str.group())
    except json.JSONDecodeError:
        pass
        
    # Try extracting from markdown code blocks
    try:
        json_match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
    except JSONDecodeError:
        pass
        
    # Final fallback - try parsing as much as possible
    try:
        # Find the longest valid JSON prefix
        for i in range(len(text), 0, -1):
            try:
                return json.loads(text[:i])
            except JSONDecodeError:
                continue
    except Exception:
        pass
        
    raise ValueError(f"Could not extract valid JSON from response. Content:\n{text[:500]}...")

@app.route('/modify-design', methods=['POST'])
def modify_design():
    try:
        data = request.get_json()
        print("Received design modification request")
        
        if not data or 'design_json' not in data:
            return jsonify({"status": "error", "message": "No design data provided"}), 400

        # Include all properties with safeguards
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

        system_message = """You are an expert UX analyzer that suggests holistic design improvements. Return JSON with:
- "status": "success"
- "summary": "assessment considering whole design"
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

        # Robust JSON parsing with multiple fallbacks
        def parse_json_response(content):
            attempts = [
                content,
                content + '"}',
                content + '}}',
                '{' + content.split('{', 1)[-1],
                content.rsplit(',', 1)[0] + '}'
            ]
            
            for attempt in attempts:
                try:
                    return json.loads(attempt)
                except json.JSONDecodeError:
                    continue
            
            try:
                json_str = re.search(r'\{.*\}', content, re.DOTALL)
                if json_str:
                    return json.loads(json_str.group())
            except:
                pass
            
            raise ValueError("Could not parse response")

        try:
            modifications = parse_json_response(content)
            
            # Validate and clean modifications
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
                    ][:2]  # Limit to 2 changes
                }
                if clean_mod['changes']:
                    valid_modifications.append(clean_mod)

            # Save to database
            doc_id, files = modified_designs_repo.save_modification_record(
                original_data=data,
                modified_json={
                    "summary": modifications.get('summary', 'Design analysis complete'),
                    "modifications": valid_modifications
                }
            )
            
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

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)