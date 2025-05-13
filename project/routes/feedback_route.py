import pandas as pd
from flask import jsonify, request
from components.Heuristics_Component.heuristic_factory import HeuristicFactory
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository
from routes.feedback_processor import FeedbackProcessor
from routes.response_formatter import ResponseFormatter
import logging
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class FeedbackRoute:
    """Main route handler for design feedback processing"""
    def __init__(self, verbose: bool = False):
        self.figma_repository = FigmaFeaturesRepository()
        self.feedback_repository = FeedbackRepository()
        self.suggestions_repository = SuggestionsRepository()
        self.processor = FeedbackProcessor()
        self.formatter = ResponseFormatter()
        self.verbose = verbose
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    def _extract_design_info(self, data: Dict) -> Tuple[str, str, str, Dict, List[Dict], Optional[str]]:
        """Extract and validate design information from request data"""
        user_name = data.get("user_name", "Unknown User")
        design_name = data.get("design_name", "Untitled Design")
        page_name = data.get("page_name", "DefaultPage")
        frame_info = data.get("frame", {})
        elements = data.get('elements', [])
        image_data_url = data.get("imageDataUrl")
        return user_name, design_name, page_name, frame_info, elements, image_data_url

    def _check_cached_feedback(self, design_name: str, frame_name: str, 
                             content_hash: str) -> Optional[Dict]:
        """Check if cached feedback exists for the design"""
        existing_feedback = self.feedback_repository.get_feedback(design_name, frame_name)
        if existing_feedback and existing_feedback.get("content_hash") == content_hash:
            logger.debug(f"Returning cached feedback for design '{design_name}'")
            return {
                "message": "Existing feedback retrieved successfully!",
                "status": 200,
                "cached": True,
                **existing_feedback
            }
        return None

    def _check_screenshot_change(self, design_name: str, frame_name: str, 
                               frame_id: str, image_data_url: Optional[str]) -> Optional[Dict]:
        """Compare current screenshot with stored one"""
        stored_design = self.figma_repository.get_saved_design(design_name, frame_name)
        stored_image = None
        if stored_design and 'frames' in stored_design:
            for frame in stored_design['frames']:
                if frame.get('frameId') == frame_id:
                    stored_image = frame.get('image64_string')
                    break
        if stored_image and image_data_url and stored_image == image_data_url:
            logger.debug("Screenshots match - design unchanged")
            return {
                "message": "Design hasn't changed since last analysis",
                "status": 304,
                "unchanged": True
            }
        logger.debug("Screenshots differ - processing new design")
        return None

    def process_elements(self):
        """Process design elements and generate feedback"""
        if request.method == 'OPTIONS':
            return '', 200

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        try:
            # Extract design info
            user_name, design_name, page_name, frame_info, elements, image_data_url = self._extract_design_info(data)
            frame_name = frame_info.get("frameName", "")
            frame_id = frame_info.get("frameId", "")

            # Check for cached feedback
            content_hash = self.processor.generate_content_hash(elements)
            cached_response = self._check_cached_feedback(design_name, frame_name, content_hash)
            if cached_response:
                return jsonify(cached_response), 200

            # Check for screenshot changes
            screenshot_response = self._check_screenshot_change(design_name, frame_name, frame_id, image_data_url)
            if screenshot_response:
                return jsonify(screenshot_response), 304

            # Store design data
            feature_data = {
                "user_name": user_name,
                "design_name": design_name,
                "page_name": page_name,
                "frame_name": frame_name,
                "frame_id": frame_id,
                "screen_size": frame_info,
                "elements": elements,
                "image64_string": image_data_url
            }
            self.figma_repository.update_or_insert_frame(feature_data)

            # Process heuristics
            elements_df = pd.DataFrame(elements)
            screen_width = frame_info["screen_width"]
            screen_height = frame_info["screen_height"]
            logger.debug("Starting heuristic evaluation...")
            consistency, minimalist, error_handling, error_prevention = self.processor.evaluate_heuristics_parallel(
                elements_df, elements, screen_width, screen_height
            )
            recognition_feedback = self.processor.process_recognition_feedback(elements, screen_width, screen_height)

            # Prepare and store feedback
            feedback_data = {
                "error_prevention_results": error_prevention,
                "consistency_results": consistency,
                "error_handling_results": error_handling,
                "minimalist_results": self.formatter.transform_minimalist_results(minimalist),
                "content_hash": content_hash,
                "recognition_results": recognition_feedback
            }
            update_result = self.feedback_repository.update_feedback(design_name, frame_name, feedback_data)
            logger.debug(f"Feedback {'updated' if update_result.matched_count > 0 else 'created'} for design '{design_name}'")

            return jsonify(self.formatter.prepare_response(
                error_prevention, consistency, error_handling,
                self.formatter.transform_minimalist_results(minimalist), recognition_feedback
            )), 200

        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    # Removed as it is in the app to check for now 
    # def get_user_history(self):
    #     """Retrieve feedback history for a user"""
    #     data = request.get_json()
    #     if not data:
    #         return jsonify({"error": "No data received"}), 400

    #     user_name = data.get("user_name", "Unknown User")
    #     try:
    #         history = self.feedback_repository.get_user_history(user_name)
    #         self._log(f"Retrieved history for user '{user_name}'", "HISTORY")
            
    #         # Format the history data
    #         formatted_history = []
    #         for item in history:
    #             formatted_item = {
    #                 "design_name": item.get("design_name", "Untitled Design"),
    #                 "frame_name": item.get("frame_name", "Unnamed Frame"),
    #                 "date": item.get("created_at", "").strftime("%Y-%m-%d %H:%M") if item.get("created_at") else "Unknown date",
    #                 "error_prevention_score": next((score for score in [
    #                     item.get("error_prevention_results", {}).get("ErrorPreventionScore"),
    #                     item.get("error_prevention_results", {}).get("feedback", {}).get("ErrorPreventionScore")
    #                 ] if score is not None), "N/A"),
    #             }
    #             formatted_history.append(formatted_item)
            
    #         return jsonify({
    #             "status": 200,
    #             "history": formatted_history
    #         }), 200
            
    #     except Exception as e:
    #         self._log(f"Error retrieving history: {str(e)}", "ERROR")
    #         return jsonify({"error": f"Server error: {str(e)}"}), 500
        