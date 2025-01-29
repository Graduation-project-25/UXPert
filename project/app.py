from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Initialize the Flask application
app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/") 
db = client[config["DATABASE_NAME"]]  
designs_collection = db[config["COLLECTION_NAME"]]  

CORS(app, supports_credentials=True)

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

    # Create a document for MongoDB
    design_document = {
        "user_id": user_id,
        "user_name": user_name,
        "design_name": design_name,
        "elements": elements, 
        "created_at": datetime.utcnow(), 
    }

    # Log the received elements
    print(f"Received design from {user_name} ({user_id}): {design_name}")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Save to MongoDB
    result = designs_collection.insert_one(design_document)

    return jsonify({
        "message": "Design saved successfully!",
        "design_id": str(result.inserted_id),
        "status": 200
    }), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
