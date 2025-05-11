from flask import Flask, request, jsonify
import os
from flask_cors import CORS

from database.figma_features_repository import FigmaFeaturesRepository
from routes.feature_extraction import FeatureExtraction
from routes.feedback import Feedback
from routes.suggestions import Suggestions



os.environ['LOKY_MAX_CPU_COUNT'] = '4'
# Initialize Flask
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# Objects
suggestions = Suggestions()
feedback = Feedback()
feature_extraction=FeatureExtraction()
 
# Register routes
app.route('/process', methods=['POST', 'OPTIONS'])(feedback.process_elements)
app.route('/get-suggestions', methods=['POST'])(suggestions.get_suggestions())
app.route('/check-frame', methods=['POST'])(feature_extraction.check_frame())

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=3000)
