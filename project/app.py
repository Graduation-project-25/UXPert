import json
import os
import textwrap
import traceback
import pandas as pd
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import app
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository

from dotenv import load_dotenv
import base64, json, traceback
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import openai
from openai import OpenAI 
import requests
# from flask_limiter import Limiter
import json 

# limiter = Limiter(app1, key_func=lambda: 'global')

load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI Key: {openai.api_key}")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = openai.models.list()
    print("Available models:", [m.id for m in models.data])
except Exception as e:
    print("OpenAI connection failed:", str(e))

figma_repository = FigmaFeaturesRepository()       
feedback_repository = FeedbackRepository()       
# suggestion_repository = SuggestionsRepository() 
# recognition_suggestion = RecognitionSuggestions()

# Initialize Flask
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

####################To Be Removed (DB)####################
# Define output folder
data_folder = "figma_features"
output_folder = data_folder + "/extracted"
evaluation_folder = data_folder + "/evaluation"

dataset_folder = './data/raw/EGFE'
main_output_folder = dataset_folder + '/extractedFeatures'
# test_folder = main_output_folder + '/test'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    print(f"Created folder: {data_folder}")
  # Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)  # Ensure the folder exists
os.makedirs(evaluation_folder, exist_ok=True)  # Ensure the folder exists

def get_new_filename():
    """Generate a unique filename based on existing files in the extracted folder."""
    existing_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
    count = len(existing_files)  # Count current files and use it for a new filename
    return os.path.join(output_folder, f"design_{count + 1}.json")

def clean_prefix(text):
    """Remove numeric prefixes like '0:' or '1:' from text."""
    return re.sub(r'^\d+:\s*', '', str(text))

def get_latest_minimalist_results():
    """Fetch the latest minimalist evaluation results from the evaluation folder."""
    minimalist_file = os.path.join(evaluation_folder, "minimalist_evaluation.json")
    print(minimalist_file)
    if os.path.exists(minimalist_file):
        with open(minimalist_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for key, elements in data.items():
            for element in elements:  
                evaluation = element.get('evaluation', None)
                return evaluation

    return {}  # Return an empty dictionary if the file is missing

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  
    # print("Raw request body:", request.data)
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
    print(f"Received design from {user_name}: {design_name} on frame {frame_name}")

    #Convert Elements to DataFrame
    elements_df = pd.DataFrame(elements)
    print(elements_df)

    ####################To Be Removed (DB)####################
    # Fetch Latest Minimalist Evaluation
    def get_latest_minimalist_results():
        """Fetch the latest minimalist evaluation results from the evaluation folder."""
        minimalist_file = os.path.join(evaluation_folder, "minimalist_evaluation.json")
        print(minimalist_file)
        if os.path.exists(minimalist_file):
            with open(minimalist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for key, elements in data.items():
                for element in elements:  
                    evaluation = element.get('evaluation', None)
                    return evaluation

        return {}  # Return an empty dictionary if the file is missing
    ##########################################################

    try:
        # Prepare feature data
        feature_data = {
            "user_name": user_name,
            "design_name": design_name,
            "page_name": page_name,
            "frame_name": frame_name,
            "screen_size": frame_info,
            "elements": elements
        }
        recognition_feedback_list = []  # Store feedback for all elements


        #Insert data into MongoDB
        print("Attempting to insert data into MongoDB...")
        insert_result = figma_repository.update_or_insert_frame(feature_data)
        # insert_result = suggestion_repository.save_suggested_features(feature_data)
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

        # Convert elements into the expected format for heuristic evaluation
        designs_for_evaluation = [{"elements": elements_db}]

        ####################To Be Removed (DB)####################
        output_data = {
            "screen_size": frame_info,  
            "elements": elements,
        }
        output_file = get_new_filename()
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4, ensure_ascii=False)

        frame_data = latest_saved_data.get("frames", [])
        if frame_data:
            elements_df = pd.DataFrame(frame_data[0].get("elements", []))
        else:
            return jsonify({"error": "No elements found in the retrieved frame data"}), 500
        ###########################################################

        # Run heuristic evaluations
        # Get screen width and height
        screen_width = frame_info["screen_width"]  
        screen_height = frame_info["screen_height"]  

        # Call Rules
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
                recognition_feedback_list.append(recognition_feedback)  # Store feedback for each element

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
            "Feedback": cleaned_minimalist_feedback,  # List of feedback messages from Minimalist
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

        
        print("Sending to Figma:", response_data) 
        # recognition_suggestion.save_updated_elements(design_name, frame_name)
        return jsonify(response_data), 200
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500



@app.route('/modify-design', methods=['POST', 'OPTIONS'])
def modify_design():
    if request.method == 'OPTIONS':
        return Response(status=200)
    
    try:
        data = request.get_json()
        if not data or 'design_json' not in data:
            return jsonify({
                "status": "error",
                "error": "Missing design data",
                "original_image": data.get('screenshot', '')
            }), 400

        design_json = data['design_json']
        screenshot_b64 = data.get('screenshot', '')

        # Validate input structure
        if 'elements' not in design_json:
            return jsonify({
                "status": "error",
                "error": "Input design missing 'elements' array",
                "original_image": screenshot_b64
            }), 400

        # Strict prompt with JSON formatting requirements
        PROMPT = """Return ONLY valid JSON with this EXACT structure:
        {
            "modifications": [{
                "node_id": "valid_node_id",
                "property": "color|text|size|position",
                "value": "new_value",
                "heuristic": "heuristic_name",
                "reason": "improvement_explanation"
            }],
            "modified_design": {
                "elements": [
                    // MUST maintain original structure
                ]
            }
        }

        Important rules:
        1. NEVER truncate the JSON
        2. Ensure all strings are properly escaped
        3. Close all brackets and quotes
        4. Don't include any markdown formatting
        5. Don't include any explanatory text outside the JSON

        Analyze this design against Nielsen's 10 heuristics:
        1. Visibility of system status
        2. Match between system and real world
        3. User control and freedom
        4. Consistency and standards
        5. Error prevention
        6. Recognition rather than recall
        7. Flexibility and efficiency of use
        8. Aesthetic and minimalist design
        9. Help users recognize, diagnose and recover from errors
        10. Help and documentation

        Current Design:\n""" + json.dumps(design_json, indent=2)

        # Call GPT-4o with strict JSON response format
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a JSON generator. Return ONLY complete, valid JSON. Never truncate the response."
            }, {
                "role": "user",
                "content": PROMPT
            }],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for more deterministic output
            max_tokens=4000   # Increased token limit for complete responses
        )

        # Get and log the raw response
        response_content = response.choices[0].message.content
        print("Full AI Response:", response_content)

        def safe_parse(json_str: str):
            """Robust JSON parsing with multiple fallbacks"""
            try:
                # First try direct parse
                return json.loads(json_str)
            except json.JSONDecodeError as e1:
                print(f"First parse failed: {str(e1)}")
                # Try cleaning common issues
                cleaned = json_str.strip()
                cleaned = re.sub(r'^```json|```$', '', cleaned)  # Remove markdown
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError as e2:
                    print(f"Second parse failed: {str(e2)}")
                    # Try to extract valid JSON portion
                    start = max(0, cleaned.find('{'))
                    end = cleaned.rfind('}') + 1
                    if start >= 0 and end > start:
                        try:
                            return json.loads(cleaned[start:end])
                        except json.JSONDecodeError as e3:
                            print(f"Partial parse failed: {str(e3)}")
                            raise ValueError(f"Could not parse JSON: {str(e3)}")
                    raise ValueError(f"Could not parse JSON: {str(e2)}")

        # Parse with robust error handling
        try:
            result = safe_parse(response_content)
            
            # Validate response structure
            if not isinstance(result.get('modified_design', {}).get('elements', None), list):
                raise ValueError("Modified design missing elements array")
                
            if not isinstance(result.get('modifications', None), list):
                raise ValueError("Modifications missing or invalid")

            return jsonify({
                "status": "success",
                "modifications": result.get("modifications", []),
                "modified_design": result["modified_design"],
                "original_image": screenshot_b64

            })

        except Exception as parse_error:
            print(f"JSON Processing Error: {str(parse_error)}\n{traceback.format_exc()}")
            # Fallback - apply modifications manually if possible
            modified = design_json.copy()
            try:
                if 'modifications' in result:  # Use result if available despite parse error
                    for change in result['modifications']:
                        for elem in modified['elements']:
                            if elem['id'] == change['node_id']:
                                elem[change['property']] = change['value']
                                break
            except:
                pass
            
            return jsonify({
                "status": "partial",
                "modifications": result.get("modifications", []) if 'result' in locals() else [],
                "modified_design": modified,
                "original_image": screenshot_b64,
                "warning": f"Used fallback method: {str(parse_error)}"
            })

    except Exception as e:
        print(f"Server Error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "original_image": screenshot_b64 if 'screenshot_b64' in locals() else "",
            "ai_response": response_content if 'response_content' in locals() else None
        }), 500
    
    
def rgb_to_hex(rgb_dict):
    """Convert RGB dictionary to hex string"""
    try:
        r = int(rgb_dict.get('r', 0) * 255)
        g = int(rgb_dict.get('g', 0) * 255)
        b = int(rgb_dict.get('b', 0) * 255)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    except:
        return "#000000"
@app.route('/proxy-image')
def proxy_image():
    try:
        image_url = request.args.get('url')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(image_url, headers=headers, stream=True)
        return Response(response.iter_content(chunk_size=1024), 
                      content_type=response.headers['Content-Type'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)