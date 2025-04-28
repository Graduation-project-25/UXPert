from flask import Flask
from flask_cors import CORS
from routes.suggestions import Suggestions
from routes.process_routes import process_elements
from routes.modify_routes import modify_design

# Initialize Flask
app = Flask(__name__, static_folder = "frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})  

# Objects
suggestions = Suggestions()
suggestions.generate_image("Project 1.png")
# suggestions.analyze_design("Project 1.png")

# Register routes
app.route('/process', methods=['POST', 'OPTIONS'])(process_elements)
app.route('/modify-design', methods=['POST'])(modify_design)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)