from flask import jsonify, request
from database.figma_features_repository import FigmaFeaturesRepository
from components.Suggestions_Component.suggestions import Suggestions as suggest


class SuggestionsRoute:
    def get_suggestions(self):
        try:
            data = request.get_json()
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
            }

            # Get the original image
            repo = FigmaFeaturesRepository()
            frame_image = repo.get_image_by_frame_id(feature_data['design_name'], feature_data['frame_id'])
            
            if not frame_image:
                return jsonify({'error': 'Original image not found'}), 404

            # Generate suggestions
            suggestions = suggest(frame_image, feature_data)
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
