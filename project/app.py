from flask import Flask, Request, request, jsonify
import os
from flask_cors import CORS
from database.feedback_repository import FeedbackRepository
from database import feedback_repository
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository
from routes.feature_extraction_route import FeatureExtractionRoute
from routes.feedback_route import FeedbackRoute
from routes.suggestions_route import SuggestionsRoute
from components.Suggestions_Component.suggestions import Suggestions


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
# app.route('/get-history', methods=['POST'])(feedback.get_user_history)
@app.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    try:
        data = request.get_json()
        force_refresh = data.get('force_refresh', False)
        
      
        # Extract Design Information
        user_name = data.get("userName", "Unknown User")
        design_name = data.get("designName", "Untitled Design")
        frame_info = data.get("frame", {})
        frame_name = frame_info.get("frameName")
        frame_id = frame_info.get("frameId")
        screen_width = frame_info.get("screen_width")
        screen_height = frame_info.get("screen_height", "")


        # Process design data
        feature_data = {
            "user_name": user_name,
            "design_name": design_name,
            "frame_name": frame_name,
            "frame_id": frame_id,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "force_refresh": force_refresh 
        }
        print(feature_data)



        # Get the original image
        repo = FigmaFeaturesRepository()
        frame_image = repo.get_image_by_frame_id(feature_data['design_name'], feature_data['frame_id'])
        
        if not frame_image:
            return jsonify({'error': 'Original image not found'}), 404

        # Generate suggestions
        suggestions = Suggestions(frame_image, feature_data)
        text_suggestions = suggestions.analyze_design()
        
        # Generate and save the modified image (only if needed)
        modified_image_b64 = suggestions.generate_suggested_image(text_suggestions)
        
        # Get the original image data URL for display
        original_image_url = f"data:image/png;base64,{frame_image}" if not frame_image.startswith('data:image') else frame_image
        
        return jsonify({
            'status': 'success',
            'suggestions': text_suggestions,
            'modified_image': modified_image_b64,
            'original_image': original_image_url
        }), 200
        
    except Exception as e:
        print(f"Error in get_suggestions: {str(e)}")
        return jsonify({'error': str(e)}), 500
# (suggestions.get_suggestions)
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
    
   
@app.post("/get-suggestions-history")
def get_suggestions_history():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    repo = SuggestionsRepository()
    try:
        # Get full history from repository
        full_history = repo.get_suggestions_history(
            data["design_name"],
            data["frame_id"],
            data["user_name"]
        )
        
        # Format the history for frontend compatibility
        formatted_history = []
        for item in full_history:
            history_item = {
                "timestamp": item["timestamp"],
                "type": item["type"]
            }
            
            # Handle text suggestions
            if item["type"] == "text":
                history_item["text"] = item["data"]
            
            # Handle image suggestions
            elif item["type"] == "image":
                image_data = item["data"]
                if not image_data.startswith('data:image'):
                    image_data = f"data:image/png;base64,{image_data}"
                history_item["image_data"] = image_data
                history_item["image_hash"] = item.get("image_hash")
            
            formatted_history.append(history_item)
        
        return jsonify({
            "status": "success", 
            "history": formatted_history or []  # Ensure empty array if no history
        })
        
    except KeyError as e:
        return jsonify({
            "error": f"Missing required field: {str(e)}",
            "status": "error"
        }), 400
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.post("/get-image-history")
async def get_image_history(request: Request):
    data = await request.json()
    repo = SuggestionsRepository()
    
    history = repo.get_image_history(
        data["design_name"],
        data["frame_id"],
        data["user_name"]
    )
    
    return {"status": "success", "history": history}

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=3000)