from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from database.feedback_repository import FeedbackRepository
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

#  
# Register routes
app.route('/process', methods=['POST', 'OPTIONS'])(feedback.process_elements)
# app.route('/get-history', methods=['POST'])(feedback.get_user_history)
app.route('/get-suggestions', methods=['POST'])(suggestions.get_suggestions)
app.route('/check-frame', methods=['POST'])(feature_extraction.check_frame)

@app.route('/get-history', methods=['POST'])
def get_user_history():
    """Get feedback history for the current user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    user_name = data.get("user_name", "Unknown User")

    try:
        # Create repository instance
        repository = FeedbackRepository()
        history = repository.get_user_history(user_name)
        print(f"Retrieved history for user '{user_name}'")  # Debug log

        # Format the history data
        formatted_history = []
        for item in history:
            formatted_item = {
                "design_name": item.get("design_name", "Untitled Design"),
                "frame_name": item.get("frame_name", "Unnamed Frame"),
                "date": item.get("created_at", "").strftime("%Y-%m-%d %H:%M") if item.get("created_at") else "Unknown date",
                "error_prevention_score": next(
                    (score for score in [
                        item.get("error_prevention_results", {}).get("ErrorPreventionScore"),
                        item.get("error_prevention_results", {}).get("feedback", {}).get("ErrorPreventionScore")
                    ] if score is not None),
                    "N/A"
                )
            }
            formatted_history.append(formatted_item)
        
        return jsonify({
            "status": 200,
            "history": formatted_history
        }), 200
        
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")  # Debug log
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    
    
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=3000)