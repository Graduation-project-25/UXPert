from datetime import datetime

from urllib import response
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
# Connect to MongoDB (Replace with your MongoDB URL)
client = MongoClient("mongodb://localhost:27017/") 
db = client[config["DATABASE_NAME"]]  # Database name
designs_collection = db[config["COLLECTION_NAME"]]  # Collection name


# Enable CORS with credentials support
CORS(app, supports_credentials=True)

# Define the '/process' route to handle POST and OPTIONS requests
@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        # Handle preflight request for CORS
        return '', 200  # Respond with HTTP 200 for preflight

    # Parse JSON data from the request
    data = request.get_json()
    user_id = data.get("user_id")
    elements = data.get('elements', [])
    design_name = data.get("design_name", "Untitled Design")
    
    if not user_id or not elements:
        return jsonify({"error": "Missing user_id or elements"}), 400

    # Create a document for MongoDB
    design_document = {
        "user_id": user_id,  # Link design to user
        "elements": elements, 
        "design_name": design_name,
        "created_at": datetime.utcnow(), # Store extracted UI elements
    }
    
    # Log the received elements to the console
    print("Received elements from Figma plugin:")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Send a response back to the client
    result = designs_collection.insert_one(design_document)

    return jsonify({"message": "Design saved successfully!", "design_id": str(result.inserted_id), "message":"Elements logged successfully!" ,"status" :200})
    # return "Elements logged successfully!", 200

# Add a simple route for the root path
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200
# @app.route("/designs/<user_id>", methods=["GET"])
# def get_user_designs(user_id):
#     user_designs = list(designs_collection.find({"user_id": user_id}, {"_id": 0}))
#     return jsonify(user_designs)
# Run the application
if __name__ == '__main__':
    app.run(debug=True,port=3000)
