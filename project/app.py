import json
import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from components.Heuristics_Component.heuristic_rules.ErrorHandling import ErrorHandling
from components.Heuristics_Component.heuristic_rules.ErrorPrevention import ErrorPrevention
from components.Heuristics_Component.heuristic_rules.consistency import Consistency
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Heuristics_Component.heuristics_evaluation.minimalist_evaluation import MinimalistEvaluation
from components.Suggestion_Component.recognition_suggestion import RecognitionSuggestions
from database.figma_features_repository import FigmaFeaturesRepository
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

        minimalist_evaluator = MinimalistEvaluation()
        minimalist_results = minimalist_evaluator.evaluate_rule(output_folder, evaluation_folder)
        minimalist_feedback_list = get_latest_minimalist_results()
        # minimalist_results = minimalist_evaluator.evaluate_rule(elements_df)

        
        error_handling = HeuristicFactory.check_rule("errorHandling")
        error_handling_results = error_handling.evaluate_rule(elements_df)
        
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
            "WhiteSpaceRatio": minimalist_feedback_list[0] if len(minimalist_feedback_list) > 0 else "No data",
            "ElementDensity": minimalist_feedback_list[1] if len(minimalist_feedback_list) > 1 else "No data",
            "IrrelevantElements": minimalist_feedback_list[2] if len(minimalist_feedback_list) > 2 else "No data",
            # "FinalScore": minimalist_feedback_list[3] if len(minimalist_feedback_list) > 3 else "No data",
            "Feedback" : minimalist_results
        }

        # print(f"Consistency evaluation feedback: {consistency_feedback}")
        # print(f"Error Prevention feedback:{error_feedback}")
        # print(f"Error handlying feedback: {error_handling_feedback}")
        # print(f"minimalist evaluation feedback: {minimalist_feedback}")    
   
        feedback_data = {
            "error_prevention_results": error_prevention_results,
            "consistency_results": consistency_results,
            "error_handling_results": error_handling_results,
            "minimalist_results": minimalist_feedback_list
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
            "minimalist_results": minimalist_feedback
        }
        print("Sending to Figma:", response_data) 
        recognition_suggestion.save_updated_elements(design_name, frame_name)
        return jsonify(response_data), 200
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)


