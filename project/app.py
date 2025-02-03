import json
import pandas as pd  # Import pandas
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os
from components.Feedback_Generator_Component.heuristics.consistency import Consistency

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Initialize the Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Define the directory to store the design data
designs_dir = 'designs_data'
if not os.path.exists(designs_dir):
    os.makedirs(designs_dir)  # Create the directory if it doesn't exist

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  

    # Parse JSON data from the request
    data = request.get_json()
    user_id = data.get("user_id", "unknown_user")
    user_name = data.get("user_name", "Unknown User")
    design_name = data.get("design_name", "Untitled Design")
    elements = data.get('elements', [])

    if not user_id or not elements:
        return jsonify({"error": "Missing user_id or elements"}), 400

    # Create a design document
    design_document = {
        "user_id": user_id,
        "user_name": user_name,
        "design_name": design_name,
        "elements": elements, 
        "created_at": datetime.utcnow().isoformat(),
    }

    # Log the received elements
    print(f"Received design from {user_name} ({user_id}): {design_name}")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Convert the elements to a pandas DataFrame
    elements_df = pd.DataFrame(elements)

    # Now, evaluate consistency based on the model
    consistency_evaluator = Consistency()
    consistency_results = consistency_evaluator.evaluate_rule(elements_df)

    # Check the structure of consistency_results
    print(f"Consistency Results: {consistency_results}")

    # Generate user-friendly consistency feedback
    consistency_feedback = generate_consistency_feedback(consistency_results)

    # Define the file path for the design
    design_file_path = os.path.join(designs_dir, f"{design_name}.json")

    # Check if a design file already exists with the same name
    if os.path.exists(design_file_path):
        # If exists, read and overwrite the file with the new design data
        with open(design_file_path, 'r') as file:
            design_data = json.load(file)

        # Replace the design's consistency result with the new one
        design_document["consistency"] = consistency_results
        design_data["consistency"] = consistency_results  # Update consistency in the design

        # Write the updated design data back to the same file
        with open(design_file_path, 'w') as file:
            json.dump(design_data, file, indent=4)
    else:
        # If file does not exist, create a new file with the design name
        design_document["consistency"] = consistency_results
        with open(design_file_path, 'w') as file:
            json.dump(design_document, file, indent=4)

    return jsonify({
        "message": "Design saved and evaluated successfully!",
        "status": 200,
        "consistency": consistency_results,  # Include the consistency evaluation in the response
        "consistency_feedback": consistency_feedback  # Include the user-friendly consistency feedback
    }), 200

def generate_consistency_feedback(consistency_results):
    """
    Generate user-friendly feedback based on the consistency evaluation results.
    Modify this function according to your evaluation logic.
    """
    feedback = []

    # Check if consistency_results is a list of dictionaries or strings
    if isinstance(consistency_results, list):
        for result in consistency_results:
            # If it's a dictionary, handle it accordingly
            if isinstance(result, dict):
                if result.get("status") == "pass":
                    feedback.append(f"✔ {result['rule']} passed!")
                else:
                    feedback.append(f"✘ {result['rule']} failed. Reason: {result['issue']}")
            else:
                # If it's a string (e.g., "pass" or "fail"), handle that
                feedback.append(f"Result: {result}")
    else:
        feedback.append(f"Unknown consistency result format: {consistency_results}")

    # Combine all feedback into a single string
    return "\n".join(feedback)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
