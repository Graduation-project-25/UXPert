from flask import jsonify, request
from database.figma_features_repository import FigmaFeaturesRepository


class FeatureExtraction:
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
