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

# Initialize Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Define output folder``
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
# @app.route("/logs", methods=["POST"])
# def receive_logs():
#     log_data = request.json.get("message", "No message received")
#     print("LOG FROM FIGMA:", log_data)
#     return "", 200  # Send back a success response

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  
    print("Raw request body:", request.data)
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data received"}), 400

    user_name = data.get("user_name", "Unknown User")
    design_name = data.get("design_name", "Untitled Design")
    page_name = data.get("page_name", "DefaultPage")
    frame_info = data.get("frame", {})
    elements = data.get('elements', [])
    if not elements:
        return jsonify({"error": "No elements found"}), 400
    frame_name = frame_info.get("frameName", "")  # Get the frame name
    print(f"Received design from {user_name}: {design_name} on frame {frame_name}")

    

    # Convert elements to DataFrame
    elements_df = pd.DataFrame(elements)
    print(elements_df)
    # Get the latest minimalist evaluation file
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


    try: 
        output_data = {
            "screen_size": frame_info,  
            "elements": elements,
            # "consistency_results": consistency_feedback,
            # "error_prevention_results": error_feedback,
            # "error_handling_results": error_handling_feedback
        }
        output_file = get_new_filename()
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4, ensure_ascii=False)

        
        
        # Evaluate consistency
        consistency_evaluator = Consistency() 
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)
        
        error_prevention = ErrorPrevention()
        error_prevention_results = error_prevention.evaluate_rule(elements_df)
        
        minimalist_evaluator = MinimalistEvaluation()
        minimalist_evaluator.evaluate_rule(output_folder, evaluation_folder)
        minimalist_feedback_list = get_latest_minimalist_results()

        # print("minimalist_feedback")
        # print(minimalist_feedback)
        error_handling = ErrorHandling()
        error_handling_results = error_handling.evaluate_rule(elements_df)


        # Prepare human-readable feedback
        consistency_feedback = {
            "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
            "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
            "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
            "TotalConsistency": f"Total consistency score is {consistency_results.get('TotalConsistency', 0)}%.",
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
            "Feedback": error_handling_results.get("Feedback", {})
        }
        minimalist_feedback = {
            "WhiteSpaceRatio": minimalist_feedback_list[0] if len(minimalist_feedback_list) > 0 else "No data",
            "ElementDensity": minimalist_feedback_list[1] if len(minimalist_feedback_list) > 1 else "No data",
            "IrrelevantElements": minimalist_feedback_list[2] if len(minimalist_feedback_list) > 2 else "No data",
            "FinalScore": minimalist_feedback_list[3] if len(minimalist_feedback_list) > 3 else "No data",
        }

        print(f"Consistency evaluation feedback: {consistency_feedback}")
        print(f"Error Prevention feedback:{error_feedback}")
        print(f"Error handlying feedback: {error_handling_feedback}")
        print(f"minimalist evaluation feedback: {minimalist_feedback}")    
   

        response_data = {
            "message": "Design processed successfully!",
            "status": 200,
            "consistency_results": consistency_feedback,
            "error_prevention_results": error_feedback,
            "error_handling_results": error_handling_feedback,
            "minimalist_results": minimalist_feedback
        }
        print("Sending to Figma:", response_data)  # ✅ DEBUG LINE

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during processing."}), 500

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
