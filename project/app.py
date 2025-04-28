from flask import Flask
from flask_cors import CORS
from routes.suggestions import Suggestions
from routes.feedback import Feedback

# Initialize Flask
app = Flask(__name__, static_folder = "frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})  

# Objects
suggestions = Suggestions()
feedback = Feedback()


# Register routes
app.route('/process', methods=['POST', 'OPTIONS'])(feedback.process_elements)
app.route('/modify-design', methods=['POST'])(suggestions.generate_suggestions)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)