import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Initialize the Flask application
app = Flask(__name__)

CORS(app, supports_credentials=True)

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  

    # Parse JSON data from the request
    data = request.get_json()
    user_name = data.get('user_name', "Unknown User")
    design_name = data.get('design_name', "Untitled Design")
    elements = data.get('elements', [])

    if not elements:
        return jsonify({"error": "Missing user_name or elements"}), 400

    # Log the received elements
    print(f"Received design from {user_name} : {design_name}")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Save the features to a JSON file
    features = {
        "user_name": user_name,
        "design_name": design_name,
        "elements": elements,
        
    }

    with open('design_features.json', 'w') as json_file:
        json.dump(features, json_file, indent=4)
    
    print("Design features have been saved to 'design_features.json'.")

    return jsonify({
        "message": "Design features saved successfully!",
        "status": 200
    }), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
