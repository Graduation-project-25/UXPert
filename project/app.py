import json
import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from components.Heuristics_Component.heuristic_rules.consistency import Consistency

# Initialize Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Define output folder
OUTPUT_FOLDER = "project/data/figma_features"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Ensure the folder exists
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "output.json")  # Save in folder

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
        consistency_evaluator = Consistency()
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)

        print(f"Consistency evaluation results: {consistency_results}")

        # Prepare human-readable feedback
        feedback = {
            "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
            "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
            "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
            "TotalConsistency": f"Total consistency score is {consistency_results.get('TotalConsistency', 0)}%.",
            "Feedback": consistency_results.get('Feedback', {})
        }

       
        output_data = {
            "user_name": user_name,
            "design_name": design_name,
            "frame": frame_info,  
            "elements": elements,
            "consistency_results": feedback 
        }

        with open(OUTPUT_FILE, "w", encoding="utf-8") as json_file:
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
