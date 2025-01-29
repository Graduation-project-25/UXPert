from flask import Flask, request
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)

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
    elements = data.get('elements', [])

    # Log the received elements to the console
    print("Received elements from Figma plugin:")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Send a response back to the client
    return "Elements logged successfully!", 200

# Add a simple route for the root path
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

# Run the application
if __name__ == '__main__':
    app.run(port=3000)
