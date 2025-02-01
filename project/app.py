import json
import pandas as pd  # Import pandas
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

from components.Feedback_Generator_Component.heuristics.consistency import Consistency

# Import the Consistency class

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Initialize the Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Define the JSON file path
json_file_path = 'designs_data.json'

# Ensure the JSON file exists
if not os.path.exists(json_file_path):
    with open(json_file_path, 'w') as file:
        json.dump([], file)  # Initialize with an empty list

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

    # Read the current contents of the JSON file
    with open(json_file_path, 'r') as file:
        designs_data = json.load(file)

    # Append the new design data along with consistency results
    design_document["consistency"] = consistency_results
    designs_data.append(design_document)  # Append the new design document

    # Write the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(designs_data, file, indent=4)

    return jsonify({
        "message": "Design saved and evaluated successfully!",
        "status": 200,
        "consistency": consistency_results  # Include the consistency evaluation in the response
    }), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
