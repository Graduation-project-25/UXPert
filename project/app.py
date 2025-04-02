import json
import os
import traceback
import pandas as pd
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import app
from components.Heuristics_Component.heuristic_rules.ErrorPrevention import ErrorPrevention
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Suggestion_Component.recognition_suggestion import RecognitionSuggestions
from components.Heuristics_Component.heuristics_testing.recognition_testing import RecognitionTesting
from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist  # Added import for Minimalist
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository

from dotenv import load_dotenv
import base64, json, traceback
import openai
from openai import OpenAI 
import requests
# from flask_limiter import Limiter

# limiter = Limiter(app1, key_func=lambda: 'global')

load_dotenv()  
# openai.api_key = os.getenv("OPENAI_API_KEY")
# print(f"OpenAI Key: {openai.api_key}")
# client = OpenAI()

# Add this to your Flask app startup
# try:
#     models = openai.models.list()
#     print("Available models:", [m.id for m in models.data])
# except Exception as e:
#     print("OpenAI connection failed:", str(e))

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
########################################################## 



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
        consistency_evaluator = HeuristicFactory.check_rule("consistency")
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)

        error_prevention_evaluator = ErrorPrevention(figma_repository)
        error_prevention_results = error_prevention_evaluator.evaluate_rule(elements_db)
        print("Error Prevention Results:", error_prevention_results)

        # Use Minimalist class directly instead of MinimalistEvaluation
        screen_width = frame_info.get("width", 1920)  # Default screen width
        screen_height = frame_info.get("height", 1080)  # Default screen height
        minimalist_evaluator = Minimalist()  # Initialize Minimalist
        minimalist_feedback, minimalist_score = minimalist_evaluator.evaluate_rule({"elements": elements}, screen_width, screen_height)  # Evaluate directly

        error_handling = HeuristicFactory.check_rule("errorHandling")
        error_handling_results = error_handling.evaluate_rule(elements_df)

        recognition__evaluator = RecognitionTesting()
        # recognition_results = recognition__evaluator.evaluate_rule_test(test_folder , evaluation_folder)
        
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
        minimalist_feedback_dict = {
            "Feedback": minimalist_feedback,  # List of feedback messages from Minimalist
            # "Score": f"Final Score: {minimalist_score:.2f}%"  # Score from Minimalist
        }

        # recognition_feedback = {
        #     "Feedback": recognition_results
        # }

        # print(f"Consistency evaluation feedback: {consistency_feedback}")
        # print(f"Error Prevention feedback:{error_feedback}")
        # print(f"Error handlying feedback: {error_handling_feedback}")
        # print(f"minimalist evaluation feedback: {minimalist_feedback}")    
   
        feedback_data = {
            "error_prevention_results": error_prevention_results,
            "consistency_results": consistency_results,
            "error_handling_results": error_handling_results,
            "minimalist_results": minimalist_feedback_dict,  # Use new dict
            # "recognition_results": recognition_results
        }
        

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
            "minimalist_results": minimalist_feedback_dict,  # Use new dict
            # "recognition_results": recognition_feedback
        }
        print("Sending to Figma:", response_data) 
        # recognition_suggestion.save_updated_elements(design_name, frame_name)
        return jsonify(response_data), 200
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/modify-design', methods=['POST'])
def modify_design():
    try:
        print("Received modify-design request")  # Debug log
        data = request.get_json()
        if not data or 'screenshot' not in data or 'elements' not in data:
            print("Missing required data")  # Debug log
            return jsonify({"error": "Missing required data"}), 400

        screenshot_b64 = data['screenshot'].split(',')[1]
        figma_json = data['elements']
        print(f"Elements received: {json.dumps(figma_json, indent=2)[:500]}...")  # Debug log

        NIELSEN_PROMPT = """Analyze this UI design against the 10 UI/UX Nielsen's heuristics
        Return JSON with:
        - "issues": [{"heuristic": 1, "element": "button1", "problem": "No loading indicator"}]
        - "changes": [{"element": "button1", "property": "color", "new_value": "#3366FF"}]
        - "dalle_prompt": "Redesign description for DALL-E"
        """

        print("Calling GPT-4o...")  # Debug log
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": f"{NIELSEN_PROMPT}\n\nCurrent Design:\n{json.dumps(figma_json)}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        
        ai_response = json.loads(response.choices[0].message.content)
        print(f"AI Response: {json.dumps(ai_response, indent=2)}")  # Debug log

        print("Generating DALL-E image...")  # Debug log
        img_response = client.images.generate(
            model="dall-e-3",
            prompt=f"Redesign this UI to fix Nielsen heuristic violations: {ai_response.get('dalle_prompt', 'Improve UI based on Nielsen heuristics')}",
            size="1024x1024",
            quality="hd"
        )
        print(f"DALL-E Response: {img_response}")  # Debug log
        dalle_url = img_response.data[0].url
        image_response = requests.get(dalle_url)
        image_bytes = image_response.content
        modified_image_b64 = base64.b64encode(image_bytes).decode('utf-8')

       
        # Build instructions array
        instructions = []
        if 'issues' in ai_response:
            instructions.extend([f"Heuristic {issue.get('heuristic', '?')}: {issue.get('problem', 'No problem description')}" 
                               for issue in ai_response['issues']])
        if 'dalle_prompt' in ai_response:
            instructions.append(ai_response['dalle_prompt'])
        if not instructions:
            instructions.append("No specific instructions provided")

        return jsonify({
            "status": "success",
            "modified_image": f"data:image/png;base64,{modified_image_b64}",  # Now sending as base64
            "modified_json": ai_response.get('changes', []),
            "analysis": ai_response.get('issues', []),
            "instructions": instructions
        })

        
    except Exception as e:
        print(f"Error: {str(e)}\n{traceback.format_exc()}")  # Debug log
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
    
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


