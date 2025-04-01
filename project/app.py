import json
import os
import traceback
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import app
from components.Heuristics_Component.heuristic_rules.ErrorHandling import ErrorHandling
from components.Heuristics_Component.heuristic_rules.ErrorPrevention import ErrorPrevention
from components.Heuristics_Component.heuristic_rules.consistency import Consistency
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Heuristics_Component.heuristics_evaluation.minimalist_evaluation import MinimalistEvaluation
from components.Suggestion_Component.recognition_suggestion import RecognitionSuggestions
from components.Heuristics_Component.heuristics_testing.recognition_testing import RecognitionTesting
from database.figma_features_repository import FigmaFeaturesRepository
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image
import openai
import requests
from flask_limiter import Limiter
from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist  # Added import for Minimalist

# limiter = Limiter(app1, key_func=lambda: 'global')

load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI Key: {openai.api_key}")
# Add this to your Flask app startup
try:
    models = openai.models.list()
    print("Available models:", [m.id for m in models.data])
except Exception as e:
    print("OpenAI connection failed:", str(e))
from database.suggestions_repository import SuggestionsRepository

figma_repository = FigmaFeaturesRepository()       
suggestion_repository = SuggestionsRepository() 
recognition_suggestion = RecognitionSuggestions()

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
test_folder = main_output_folder + '/test'
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
        insert_result = suggestion_repository.save_suggested_features(feature_data)
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
        recognition_results = recognition__evaluator.evaluate_rule_test(test_folder , evaluation_folder)
        
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
            "Score": f"Final Score: {minimalist_score:.2f}%"  # Score from Minimalist
        }

        recognition_feedback = {
            "Feedback": recognition_results
        }

        # print(f"Consistency evaluation feedback: {consistency_feedback}")
        # print(f"Error Prevention feedback:{error_feedback}")
        # print(f"Error handlying feedback: {error_handling_feedback}")
        # print(f"minimalist evaluation feedback: {minimalist_feedback}")    
   
        feedback_data = {
            "error_prevention_results": error_prevention_results,
            "consistency_results": consistency_results,
            "error_handling_results": error_handling_results,
            "minimalist_results": minimalist_feedback_dict,  # Use new dict
            "recognition_results": recognition_results
        }
        

        update_result = figma_repository.update_feedback(design_name, frame_name, feedback_data)

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
            "recognition_results": recognition_feedback
        }
        print("Sending to Figma:", response_data) 
        recognition_suggestion.save_updated_elements(design_name, frame_name)
        return jsonify(response_data), 200
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# @app.route('/modify-design', methods=['POST', 'OPTIONS'])
# def modify_design():
#     if request.method == 'OPTIONS':
#         return '', 200
        
#     try:
#         print("\n=== NEW REQUEST ===")
#         data = request.get_json()
#         print("Received data keys:", data.keys() if data else "No data")
        
#         # Validate required fields
#         if not data or 'screenshot' not in data or 'feedback' not in data:
#             print("Missing required fields")
#             return jsonify({"error": "Missing required fields"}), 400
            
#         screenshot_base64 = data['screenshot']
#         heuristic_feedback = data['feedback']
#         design_elements = data.get('elements', [])
        
#         # Validate image
#         try:
#             print("Validating image...")
#             image_data = base64.b64decode(screenshot_base64.split(',')[1])
#             img = Image.open(BytesIO(image_data))
#             print(f"Image validated: {img.format}, {img.size}")
#         except Exception as e:
#             print(f"Image validation failed: {str(e)}")
#             return jsonify({"error": f"Invalid image: {str(e)}"}), 400

#         # Prepare prompt
#         prompt = f"""Analyze this UI design based on Nielsen's heuristics:
#         {json.dumps(heuristic_feedback, indent=2)}
        
#         Elements:
#         {json.dumps(design_elements, indent=2)}
        
#         Provide specific visual improvements in markdown format."""
        
#         print("Attempting OpenAI API call...")
        
#         try:
#             # Skip vision models and go straight to text-only
#             print("Using GPT-3.5-turbo (text-only fallback)")
#             response = openai.chat.completions.create(
#                 model="gpt-3.5-turbo-0125",
#                 messages=[{
#                     "role": "user",
#                     "content": prompt  # Text-only prompt
#                 }],
#                 max_tokens=1000,
#             )
#             print("OpenAI API call successful with gpt-4o")
            
#         except Exception as e:
#             print(f"gpt-4o failed, trying gpt-4o-2024-05-13. Error: {str(e)}")
#             try:
#                 response = openai.chat.completions.create(
#                     model="gpt-4o-2024-05-13",
#                     messages=[{
#                         "role": "user",
#                         "content": [
#                             {"type": "text", "text": prompt},
#                             {
#                                 "type": "image_url",
#                                 "image_url": {
#                                     "url": f"data:image/png;base64,{screenshot_base64}",
#                                 },
#                             },
#                         ],
#                     }],
#                     max_tokens=1000,
#                 )
#                 print("OpenAI API call successful with gpt-4o-2024-05-13")
                
#             except Exception as e:
#                 print(f"Vision models failed, falling back to text-only. Error: {str(e)}")
#                 response = openai.chat.completions.create(
#                     model="gpt-3.5-turbo-0125",
#                     messages=[{"role": "user", "content": prompt}],
#                     max_tokens=1000,
#                 )
#                 print("Text-only API call successful")

#         instructions = response.choices[0].message.content
#         print("Successfully generated modifications")
        
#         return jsonify({
#             "status": "success",
#             "modification_instructions": instructions,
#             "original_screenshot": screenshot_base64,
#             "modified_screenshot": None
#         })
        
#     except Exception as e:
#         print(f"CRITICAL ERROR: {str(e)}")
#         return jsonify({
#             "error": str(e),
#             "message": "Failed to process design modifications",
#             "traceback": traceback.format_exc()
#         }), 500

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)


