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
import concurrent.futures

class Feedback:
    def __init__(self, verbose=False):
        self.figma_repository = FigmaFeaturesRepository()
        self.suggestions_repository = SuggestionsRepository()
        self.feedback_repository = FeedbackRepository()
        self.verbose = verbose  # Control whether to print logs

    def _generate_content_hash(self, elements):
        """Generate a stable hash of the design elements to detect changes"""
        elements_str = json.dumps(elements, sort_keys=True)
        return hashlib.md5(elements_str.encode()).hexdigest()

    def _log(self, message, feedback_type=None):
        """Helper method for logging (now silent by default)"""
        if self.verbose:  # Only log if verbose mode is enabled
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

    def _evaluate_heuristics_parallel(self, elements_df, elements, screen_width, screen_height):
        """Evaluate all heuristics in parallel using ThreadPoolExecutor"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Prepare evaluators
            consistency_evaluator = HeuristicFactory.check_rule("consistency")
            minimalist_evaluator = HeuristicFactory.check_rule("minimalist")
            error_handling_evaluator = HeuristicFactory.check_rule("errorHandling")
            error_prevention_evaluator = HeuristicFactory.check_rule("errorPrevention")

            # Submit all tasks
            future_consistency = executor.submit(
                consistency_evaluator.evaluate_rule, 
                elements_df
            )
            future_minimalist = executor.submit(
                minimalist_evaluator.evaluate_rule,
                {"elements": elements},
                screen_width,
                screen_height
            )
            future_error_handling = executor.submit(
                error_handling_evaluator.evaluate_rule,
                elements_df
            )
            future_error_prevention = executor.submit(
                error_prevention_evaluator.evaluate_rule,
                elements_df
            )

            # Get results
            consistency_results = future_consistency.result()
            minimalist_results, _ = future_minimalist.result()
            error_handling_results = future_error_handling.result()
            error_prevention_results = future_error_prevention.result()

            return (
                consistency_results,
                minimalist_results,
                error_handling_results,
                error_prevention_results
            )

    def _process_recognition_feedback(self, elements, screen_width, screen_height):
        """Process recognition feedback sequentially (element-by-element)"""
        recognition_feedback_list = []
        recognition_evaluator = HeuristicFactory.check_rule("recognition")
        
        for element in elements:
            recognition_results = recognition_evaluator.evaluate_rule(
                element, 
                element["type"], 
                screen_width, 
                screen_height, 
                element.get("isIconLabeled", False), 
                element["width"], 
                element["height"]
            )
            if recognition_results:
                recognition_feedback_list.append({
                    "element_id": element["id"],
                    "element_name": element.get("name", "Unnamed"),
                    "element_type": element["type"],
                    "Feedback": recognition_results,
                })
        
        return recognition_feedback_list

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

        # Prepare data for processing
        elements_df = pd.DataFrame(elements)
        screen_width = frame_info["screen_width"]
        screen_height = frame_info["screen_height"]

        try:
            # Store design data first
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
            self.figma_repository.update_or_insert_frame(feature_data)

            # Process heuristics in parallel
            self._log("Starting parallel heuristic evaluation...", "PROCESSING")
            (consistency_results,
             minimalist_results,
             error_handling_results,
             error_prevention_results) = self._evaluate_heuristics_parallel(
                elements_df, elements, screen_width, screen_height
             )

            # Process recognition feedback sequentially
            recognition_feedback_list = self._process_recognition_feedback(
                elements, screen_width, screen_height
            )

            # Prepare and save feedback
            feedback_data = {
                "error_prevention_results": error_prevention_results,
                "consistency_results": consistency_results,
                "error_handling_results": error_handling_results,
                "minimalist_results": self._transform_minimalist_results(minimalist_results),
                "content_hash": current_content_hash,
                "recognition_results": recognition_feedback_list
            }

            update_result = self.feedback_repository.update_feedback(
                design_name, 
                frame_name, 
                feedback_data
            )
            
            if update_result.matched_count > 0:
                self._log(f"Updated feedback for design '{design_name}'", "UPDATE")
            elif update_result.upserted_id:
                self._log(f"Created new feedback for design '{design_name}'", "CREATE")

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