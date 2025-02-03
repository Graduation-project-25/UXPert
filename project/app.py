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

    # Log the received elements
    print(f"Received design from {user_name} ({user_id}): {design_name}")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Convert the elements to a pandas DataFrame
    elements_df = pd.DataFrame(elements)

    # Now, evaluate consistency based on the model
    consistency_evaluator = Consistency()
    consistency_results = consistency_evaluator.evaluate_rule(elements_df)

    # Print the consistency results in the terminal
    print(f"Consistency evaluation results: {consistency_results}")

    # Return the response without saving the design
    return jsonify({
        "message": "Design processed successfully (no file saved)!",
        "status": 200,
        "consistency": consistency_results  # Include the consistency evaluation in the response
    }), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
