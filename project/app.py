from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Root route for testing connectivity
@app.route("/", methods=["GET"])
def index():
    print("Root route accessed")  # Log when the route is accessed
    return "Backend is running successfully!"

# Example route for processing data
@app.route("/process", methods=["POST"])
def process_data():
    # Parse the JSON data from the request
    data = request.json
    print("Received data:", data)  # Debugging line to inspect the incoming data

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Perform some processing (example: counting the number of elements)
    elements = data.get("elements", [])
    element_count = len(elements)

    return jsonify({
        "message": "Data processed successfully!",
        "element_count": element_count
    })

if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)



