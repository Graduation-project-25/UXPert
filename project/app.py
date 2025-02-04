import json
import pandas as pd  # Import pandas
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from components.Feedback_Generator_Component.heuristics.consistency import Consistency

# Initialize Flask
app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  

    data = request.get_json()
    user_id = data.get("user_id", "unknown_user")
    user_name = data.get("user_name", "Unknown User")
    design_name = data.get("design_name", "Untitled Design")
    elements = data.get('elements', [])

    if not user_id or not elements:
        return jsonify({"error": "Missing user_id or elements"}), 400

    print(f"Received design from {user_name} ({user_id}): {design_name}")

    elements_df = pd.DataFrame(elements)

    # Evaluate consistency
    consistency_evaluator = Consistency()
    consistency_results = consistency_evaluator.evaluate_rule(elements_df)

    print(f"Consistency evaluation results: {consistency_results}")

    return jsonify({
        "message": "Design processed successfully!",
        "status": 200,
        "consistency_results": consistency_results  
    }), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
