import pandas as pd
from flask import jsonify, request
from components.Heuristics_Component.heuristic_factory import HeuristicFactory
from components.Suggestions_Component.suggestions import Suggestions
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository
from utils.helpers import clean_prefix
from datetime import datetime
import hashlib
import json

class FeedbackRoute:
    def __init__(self):
        self.figma_repository = FigmaFeaturesRepository()
        self.suggestions_repository = SuggestionsRepository()
        self.feedback_repository = FeedbackRepository()

    def _generate_content_hash(self, elements):
        """Generate a stable hash of the design elements to detect changes"""
        elements_str = json.dumps(elements, sort_keys=True)
        return hashlib.md5(elements_str.encode()).hexdigest()

    def _log(self, message, feedback_type=None):
        """Helper method for consistent logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if feedback_type:
            print(f"[{timestamp}] [{feedback_type}] {message}")
        else:
            print(f"[{timestamp}] {message}")

    def _transform_minimalist_results(self, minimalist_results):
        """Helper method to transform minimalist results into consistent format"""
        cleaned_minimalist_feedback = []
        
        if isinstance(minimalist_results, dict):
            for key, value in minimalist_results.items():
                cleaned_key = clean_prefix(key)
                if "white space" in cleaned_key.lower():
                    issue = "White Space Ratio"
                elif "elements" in cleaned_key.lower() and "irrelevant" not in cleaned_key.lower():
                    issue = "Number of Elements"
                elif "irrelevant" in cleaned_key.lower():
                    issue = "Irrelevant Elements"
                elif "score" in cleaned_key.lower():
                    issue = "Score"
                else:
                    issue = cleaned_key
                cleaned_minimalist_feedback.append({
                    "issue": issue,
                    "feedback": clean_prefix(value) if isinstance(value, str) else str(value)
                })
        elif isinstance(minimalist_results, list):
            for item in minimalist_results:
                if isinstance(item, str):
                    cleaned_item = clean_prefix(item)
                    if "white space" in cleaned_item.lower():
                        issue = "White Space Ratio"
                    elif "elements" in cleaned_item.lower() and "irrelevant" not in cleaned_item.lower():
                        issue = "Number of Elements"
                    elif "irrelevant" in cleaned_item.lower():
                        issue = "Irrelevant Elements"
                    elif "score" in cleaned_item.lower():
                        issue = "Score"
                    else:
                        issue = "Feedback"
                    cleaned_minimalist_feedback.append({
                        "issue": issue,
                        "feedback": cleaned_item
                    })
                elif isinstance(item, dict):
                    cleaned_minimalist_feedback.append({
                        "issue": clean_prefix(item.get('issue', '')),
                        "feedback": clean_prefix(item.get('feedback', '')) if isinstance(item.get('feedback'), str) else str(item.get('feedback', ''))
                    })
        else:
            cleaned_minimalist_feedback.append({
                "issue": "Score",
                "feedback": clean_prefix(str(minimalist_results))
            })
            
        return {"Feedback": cleaned_minimalist_feedback}

    def _prepare_response_data(self, error_prevention_results, consistency_results, 
                             error_handling_results, minimalist_feedback, recognition_feedback_list):
        """Helper method to prepare standardized response data"""
        return {
            "message": "Design processed successfully!",
            "status": 200,
            "cached": False,
            "error_prevention_results": {
                "ErrorPreventionScore": f"Error Prevention Score: {error_prevention_results.get('ErrorPreventionScore', 0)}%.",
                "ValidationIssues": error_prevention_results.get("ValidationIssues", []),
                "ConfirmationIssues": error_prevention_results.get("ConfirmationIssues", []),
                "Feedback": error_prevention_results.get("Feedback", {})
            },
            "consistency_results": {
                "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
                "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
                "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
                "Feedback": consistency_results.get('Feedback', {})
            },
            "error_handling_results": {
                "ErrorHandlingScore": f"Error Handling Score: {error_handling_results.get('ErrorHandlingScore', 0)}%.",
                "ErrorIssues": error_handling_results.get("ErrorIssues", []),
                "RecoveryIssues": error_handling_results.get("RecoveryIssues", []),
                "Feedback": error_handling_results
            },
            "minimalist_results": minimalist_feedback,
            "recognition_results": recognition_feedback_list if recognition_feedback_list else []
        }

    def process_elements(self):
        if request.method == 'OPTIONS':
            return '', 200

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extract Design Information
        user_name = data.get("user_name", "Unknown User")
        design_name = data.get("design_name", "Untitled Design")
        page_name = data.get("page_name", "DefaultPage")
        frame_info = data.get("frame", {})
        frame_name = frame_info.get("frameName", "")
        frame_id = frame_info.get("frameId", "")
        elements = data.get('elements', [])
        imageDataUrl = data.get("imageDataUrl")

        if not elements:
            return jsonify({"error": "No elements found"}), 400

        # Generate content hash for current elements
        current_content_hash = self._generate_content_hash(elements)
        self._log(f"Content hash generated: {current_content_hash}", "DEBUG")

        # Check if identical feedback exists in database
        existing_feedback = self.feedback_repository.get_feedback(design_name, frame_name)
        
        if existing_feedback and existing_feedback.get("content_hash") == current_content_hash:
            self._log(f"Returning existing feedback for unchanged design '{design_name}'", "CACHED")
            return jsonify({
                "message": "Existing feedback retrieved successfully!",
                "status": 200,
                "cached": True,
                "error_prevention_results": existing_feedback.get("error_prevention_results", {}),
                "consistency_results": existing_feedback.get("consistency_results", {}),
                "error_handling_results": existing_feedback.get("error_handling_results", {}),
                "minimalist_results": existing_feedback.get("minimalist_results", {}),
                "recognition_results": existing_feedback.get("recognition_results", [])
            }), 200

        # Get the stored screenshot for this design
        stored_design = self.figma_repository.get_saved_design(design_name, frame_name)
        stored_image = None
        if stored_design and 'frames' in stored_design:
            for frame in stored_design['frames']:
                if frame.get('frameId') == frame_id:
                    stored_image = frame.get('image64_string')
                    break

        # Compare screenshots if both exist
        if stored_image and imageDataUrl:
            if stored_image == imageDataUrl:
                self._log("Screenshots match exactly - design hasn't changed", "SCREENSHOT_COMPARE")
                return jsonify({
                    "message": "Design hasn't changed since last analysis",
                    "status": 304,
                    "unchanged": True
                }), 304
            else:
                self._log("Screenshots differ - design has changed", "SCREENSHOT_COMPARE")

        # If we get here, either it's new or content has changed
        if existing_feedback:
            self._log(f"Design content changed for '{design_name}', generating new feedback", "UPDATE")
        else:
            self._log(f"Processing new feedback for design '{design_name}'", "NEW")

        # Retrieve existing elements from the database
        latest_saved_data = self.figma_repository.get_saved_design(design_name, frame_name)
        existing_elements = []
        if latest_saved_data:
            frames = latest_saved_data.get("frames", [])
            existing_elements = [elem for frame in frames for elem in frame.get("elements", [])]
        
        # Compare incoming elements with existing elements
        existing_element_ids = {elem["id"] for elem in existing_elements}
        new_elements = [elem for elem in elements if elem["id"] not in existing_element_ids]

        # Log new elements if any
        if new_elements:
            self._log("New elements found:", "INFO")
            for elem in new_elements:
                self._log(f"- Element ID: {elem['id']}, Name: {elem.get('name', 'Unnamed')}, Type: {elem.get('type', 'Unknown')}", "INFO")
        else:
            self._log("No new elements found", "INFO")

        elements_df = pd.DataFrame(elements)

        try:
            # Process design data
            feature_data = {
                "user_name": user_name,
                "design_name": design_name,
                "page_name": page_name,
                "frame_name": frame_name,
                "frame_id": frame_id,
                "screen_size": frame_info,
                "elements": elements,
                "image64_string": imageDataUrl
            }

            # Store design data
            insert_result = self.figma_repository.update_or_insert_frame(feature_data)
            
            # Get the image for suggestions
            frame_image = self.figma_repository.get_image_by_frame_id(
                feature_data["design_name"],
                feature_data["frame_id"]
            )
            if frame_image:
                self.suggestions_repository.save_original_image_id(feature_data)
            
            # Retrieve Saved Design
            latest_saved_data = self.figma_repository.get_saved_design(design_name, frame_name)
            if not latest_saved_data:
                self._log("Failed to retrieve saved design data", "ERROR")
                return jsonify({"error": "Failed to retrieve saved design data"}), 500

            # Process elements
            frames = latest_saved_data.get("frames", [])
            if not frames:
                self._log("No frames found in design", "ERROR")
                return jsonify({"error": "No frames found in the retrieved design"}), 500

            elements_list = [elem for frame in frames for elem in frame.get("elements", [])]
            if not elements_list:
                self._log("No elements found in frames", "ERROR")
                return jsonify({"error": "No elements found in the retrieved frames"}), 500

            elements_db = pd.DataFrame(elements_list)
            screen_width = frame_info["screen_width"]
            screen_height = frame_info["screen_height"]

            # Initialize evaluators
            self._log("Initializing heuristic evaluators...", "PROCESSING")
            consistency_evaluator = HeuristicFactory.check_rule("consistency")
            minimalist_evaluator = HeuristicFactory.check_rule("minimalist")
            recognition_evaluator = HeuristicFactory.check_rule("recognition")
            error_handling_evaluator = HeuristicFactory.check_rule("errorHandling")
            error_prevention_evaluator = HeuristicFactory.check_rule("errorPrevention")

            # Evaluate Rules
            self._log("Evaluating design heuristics...", "PROCESSING")
            consistency_results = consistency_evaluator.evaluate_rule(elements_df)
            minimalist_results, minimalist_score = minimalist_evaluator.evaluate_rule({"elements": elements}, screen_width, screen_height)
            error_handling_results = error_handling_evaluator.evaluate_rule(elements_df)
            error_prevention_results = error_prevention_evaluator.evaluate_rule(elements_db)
            
            # Process recognition feedback
            recognition_feedback_list = []
            for element in elements:
                recognition_results = recognition_evaluator.evaluate_rule(
                    element, 
                    element["type"], 
                    screen_width, 
                    screen_height, 
                    element["isIconLabeled"], 
                    element["width"], 
                    element["height"]
                )
                if recognition_results:
                    recognition_feedback_list.append({
                        "element_id": element["id"],
                        "element_name": element["name"],
                        "element_type": element["type"],
                        "Feedback": recognition_results,
                    })

            # Prepare feedback data with content hash
            feedback_data = {
                "error_prevention_results": error_prevention_results,
                "consistency_results": consistency_results,
                "error_handling_results": error_handling_results,
                "minimalist_results": self._transform_minimalist_results(minimalist_results),
                "content_hash": current_content_hash,
                "recognition_results": recognition_feedback_list if recognition_feedback_list else []
            }

            # Save feedback to database only if content changed or it's new
            update_result = self.feedback_repository.update_feedback(
                design_name, 
                frame_name, 
                feedback_data
            )
            
            if update_result.matched_count > 0:
                self._log(f"Updated feedback for design '{design_name}' with new content", "UPDATE")
            elif update_result.upserted_id:
                self._log(f"Created new feedback for design '{design_name}'", "CREATE")
            else:
                self._log("Failed to save feedback", "ERROR")
                return jsonify({"error": "Failed to save feedback to database"}), 500

            self._log("Feedback processing completed successfully", "SUCCESS")
            return jsonify(self._prepare_response_data(
                error_prevention_results,
                consistency_results,
                error_handling_results,
                self._transform_minimalist_results(minimalist_results),
                recognition_feedback_list
            )), 200

        except Exception as e:
            self._log(f"Processing error: {str(e)}", "ERROR")
            return jsonify({"error": f"Server error: {str(e)}"}), 500
        

    def get_user_history(self):
        """Get feedback history for the current user"""
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        user_name = data.get("user_name", "Unknown User")
        
        try:
            history = self.feedback_repository.get_user_history(user_name)
            self._log(f"Retrieved history for user '{user_name}'", "HISTORY")
            
            # Format the history data
            formatted_history = []
            for item in history:
                formatted_item = {
                    "design_name": item.get("design_name", "Untitled Design"),
                    "frame_name": item.get("frame_name", "Unnamed Frame"),
                    "date": item.get("created_at", "").strftime("%Y-%m-%d %H:%M") if item.get("created_at") else "Unknown date",
                    "error_prevention_score": next((score for score in [
                        item.get("error_prevention_results", {}).get("ErrorPreventionScore"),
                        item.get("error_prevention_results", {}).get("feedback", {}).get("ErrorPreventionScore")
                    ] if score is not None), "N/A"),
                    "minimalist_feedback": next((feedback for feedback in [
                        item.get("minimalist_results", {}).get("Feedback"),
                        item.get("minimalist_results", {}).get("feedback", {}).get("Feedback")
                    ] if feedback is not None), [])
                }
                formatted_history.append(formatted_item)
            
            return jsonify({
                "status": 200,
                "history": formatted_history
            }), 200
            
        except Exception as e:
            self._log(f"Error retrieving history: {str(e)}", "ERROR")
            return jsonify({"error": f"Server error: {str(e)}"}), 500
