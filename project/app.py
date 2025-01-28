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
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Perform some processing (example: counting the number of elements)
    elements = data.get("elements", [])
    element_count = len(elements)

    return jsonify({
        "message": "Data processed successfully!",
        "element_count": element_count
    })

# Another example route for testing success
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"success": True, "message": "Test endpoint works!"})

if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)



#     Root Route (/):

# Simple GET endpoint to confirm that the backend is running.
# The Figma plugin can use this endpoint to check the connection.
# Data Processing Route (/process):

# Example POST endpoint for processing data sent from the Figma plugin.
# Accepts JSON input with an elements array and calculates the number of elements.
# Test Route (/test):

# A basic GET endpoint to return a success message.
# Development Server:

# Runs on http://localhost:3000 to match the URL in your JavaScript code.

