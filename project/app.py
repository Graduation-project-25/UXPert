from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from components.Suggestions_Component.suggestions import Suggestions
from database.suggestions_repository import SuggestionsRepository
from routes.feedback import Feedback
from database.figma_features_repository import FigmaFeaturesRepository



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

@app.route('/check-frame', methods=['POST'])
def check_frame():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['design_name', 'frame_name', 'elements']):
            print(f"Invalid request data: {data}")
            return jsonify({'error': 'Missing required fields'}), 400

        repo = FigmaFeaturesRepository()
        saved_design = repo.get_saved_design(data['design_name'], data['frame_name'])
        print(f"Saved design: {saved_design}")
        if saved_design and saved_design.get("frames") and len(saved_design["frames"]) > 0 and saved_design["frames"][0]["elements"] == data["elements"]:
            feedback = saved_design["frames"][0].get("feedback")
            print(f"Feedback found: {feedback}")
            if feedback:
                return jsonify({'feedback': feedback}), 200
        print("No matching feedback found, returning empty response")
        return jsonify({}), 200
    except Exception as e:
        print(f"Error in check_frame: {str(e)}")
        return jsonify({'error': f'Error checking frame: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=3000)
