from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from routes.feature_extraction_route import FeatureExtractionRoute
from routes.feedback_route import FeedbackRoute
from routes.suggestions_route import SuggestionsRoute


os.environ['LOKY_MAX_CPU_COUNT'] = '4'
# Initialize Flask
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# Objects
suggestions = SuggestionsRoute()
feedback = FeedbackRoute()
feature_extraction = FeatureExtractionRoute()

 
# Register routes
app.route('/process', methods=['POST', 'OPTIONS'])(feedback.process_elements)
app.route('/get-history', methods=['POST'])(feedback.get_user_history)
app.route('/get-suggestions', methods=['POST'])(suggestions.get_suggestions)
app.route('/check-frame', methods=['POST'])(feature_extraction.check_frame)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=3000)