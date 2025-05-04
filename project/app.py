from flask import Flask
import os
from flask_cors import CORS
from components.Suggestions_Component.suggestions import Suggestions
from routes.feedback import Feedback


os.environ['LOKY_MAX_CPU_COUNT'] = '4'
# Initialize Flask
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# Objects
# suggestions = Suggestions()
# suggestions.generate_suggestions()
feedback = Feedback()

# Register routes
app.route('/process', methods=['POST', 'OPTIONS'])(feedback.process_elements)
# app.route('/modify-design', methods=['POST'])(suggestions.generate_suggestions)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=3000)
