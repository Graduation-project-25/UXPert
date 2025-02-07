import json
import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from components.Heuristics_Component.heuristic_rules.consistency import Consistency
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Heuristics_Component.heuristics_evaluation.minimalist_evaluation import MinimalistEvaluation

# Initialize Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Define output folder
data_folder = "project/data/figma_features"
output_folder = data_folder + "/extracted"
evaluation_folder = data_folder + "/evaluation"
os.makedirs(data_folder, exist_ok=True)  # Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)  # Ensure the folder exists
os.makedirs(evaluation_folder, exist_ok=True)  # Ensure the folder exists

def get_new_filename():
    """Generate a unique filename based on existing files in the extracted folder."""
    existing_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
    count = len(existing_files)  # Count current files and use it for a new filename
    return os.path.join(output_folder, f"design_{count + 1}.json")

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  

    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data received"}), 400

    user_name = data.get("user_name", "Unknown User")
    design_name = data.get("design_name", "Untitled Design")
    frame_info = data.get("frame", {})
    elements = data.get('elements', [])
    if not elements:
        return jsonify({"error": "No elements found"}), 400

    print(f"Received design from {user_name}: {design_name}")

    # Convert elements to DataFrame
    elements_df = pd.DataFrame(elements)

    try:
        # Evaluate consistency
        consistency_evaluator = HeuristicFactory.check_rule("consistency")
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)

        minimalist_evaluator = MinimalistEvaluation()
        minimalist_evaluator = minimalist_evaluator.evaluate_rule(output_folder, evaluation_folder)

        print(f"Consistency evaluation results: {consistency_results}")

        # Prepare human-readable feedback
        feedback = {
            "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
            "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
            "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
            "TotalConsistency": f"Total consistency score is {consistency_results.get('TotalConsistency', 0)}%.",
            "Minimalist": f"Minimalist is {minimalist_evaluator}",
            "Feedback": consistency_results.get('Feedback', {})
        }

       
        output_data = {
            # "user_name": user_name,
            # "design_name": design_name,
            "screen_size": frame_info,  
            "elements": elements,
            "consistency_results": feedback 
        }

        output_file = get_new_filename() # Save in folder
        # count+=1
        # print(count)
        print("*********************************************************************************************")

        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4, ensure_ascii=False)

        return jsonify({
            "message": "Design processed successfully!",
            "status": 200,
            "consistency_results": feedback
        }), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during processing."}), 500

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
