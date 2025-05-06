import pandas as pd
from flask import jsonify, request
from components.Heuristics_Component.heuristic_factory import HeuristicFactory
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository
from utils.helpers import clean_prefix
from datetime import datetime, timedelta

class Feedback:
    def __init__(self):
        self.figma_repository = FigmaFeaturesRepository()
        self.suggestions_repository = SuggestionsRepository()
        self.feedback_repository = FeedbackRepository()
        self.cache_expiry_hours = 1  # Cache feedback for 1 hour

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

        try:
            # Check for cached feedback first
            cached_response = self._check_for_cached_feedback(design_name, frame_name, elements)
            if cached_response:
                return cached_response

            # Process new feedback if no valid cache exists
            return self._process_new_feedback(
                user_name, design_name, page_name, 
                frame_info, frame_name, frame_id, 
                elements, imageDataUrl
            )

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    def _check_for_cached_feedback(self, design_name, frame_name, current_elements):
        """Check if valid cached feedback exists for this design frame"""
        existing_feedback = self.feedback_repository.get_feedback(design_name, frame_name)
        
        if not existing_feedback:
            return None

        # Check if cache is expired
        last_updated = existing_feedback.get("last_updated")
        if last_updated and isinstance(last_updated, datetime):
            if datetime.now() - last_updated > timedelta(hours=self.cache_expiry_hours):
                return None

        # Optional: Check if elements have changed (more thorough cache validation)
        cached_elements_hash = existing_feedback.get("elements_hash")
        if cached_elements_hash:
            current_hash = self._generate_elements_hash(current_elements)
            if current_hash != cached_elements_hash:
                return None

        print("Returning cached feedback")
        return self._format_cached_response(existing_feedback)

    def _process_new_feedback(self, user_name, design_name, page_name, frame_info, 
                            frame_name, frame_id, elements, imageDataUrl):
        """Process elements and generate new feedback"""
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

            recognition_feedback_list = []

            print("Attempting to insert data into MongoDB...")
            insert_result = self.figma_repository.update_or_insert_frame(feature_data)
            doc_id = self.suggestions_repository.save_original_image_id(feature_data)

            # 3. Get the image FROM THE CORRECT REPOSITORY
            frame_image = self.figma_repository.get_image_by_frame_id(
                feature_data["design_name"],
                feature_data["frame_id"]
            )
            print(frame_image)
            print("Data inserted successfully.")
            if frame_image:
                suggestions = Suggestions()
                suggestions.generate_suggestions(doc_id, frame_id)  # Uses image from suggestions repo
            if insert_result.matched_count > 0:
                print(f"Frame added to existing design: {design_name}")
            else:
                print(f"New design document created: {design_name}")

            # Retrieve Saved Design
            latest_saved_data = self.figma_repository.get_saved_design(design_name, frame_name)

            if not latest_saved_data:
                print("Failed to retrieve saved design data from MongoDB")
                return jsonify({"error": "Failed to retrieve saved design data"}), 500

            # Extract elements from the retrieved design data
            frames = latest_saved_data.get("frames", [])
            if not frames:
                return jsonify({"error": "No frames found in the retrieved design"}), 500

            elements_list = [elem for frame in frames for elem in frame.get("elements", [])]

            if not elements_list:
                return jsonify({"error": "No elements found in the retrieved frames"}), 500

            elements_db = pd.DataFrame(elements_list)

            designs_for_evaluation = [{"elements": elements_db}]

            output_data = {
                "screen_size": frame_info,
                "elements": elements,
            }

            frame_data = latest_saved_data.get("frames", [])
            if frame_data:
                elements_df = pd.DataFrame(frame_data[0].get("elements", []))
            else:
                return jsonify({"error": "No elements found in the retrieved frame data"}), 500

            screen_width = frame_info["screen_width"]
            screen_height = frame_info["screen_height"]

        # Initialize evaluators
        consistency_evaluator = HeuristicFactory.check_rule("consistency")
        minimalist_evaluator = HeuristicFactory.check_rule("minimalist")
        recognition_evaluator = HeuristicFactory.check_rule("recognition")
        error_handling_evaluator = HeuristicFactory.check_rule("errorHandling")
        error_prevention_evaluator = HeuristicFactory.check_rule("errorPrevention")

        # Evaluate Rules
        consistency_results = consistency_evaluator.evaluate_rule(elements_df)
        minimalist_results, minimalist_score = minimalist_evaluator.evaluate_rule(
            {"elements": elements}, screen_width, screen_height
        )
        error_handling_results = error_handling_evaluator.evaluate_rule(elements_df)
        error_prevention_results = error_prevention_evaluator.evaluate_rule(elements_df)
        
        recognition_feedback_list = []
        for element in elements:
            recognition_results = recognition_evaluator.evaluate_rule(
                element, element["type"], screen_width, screen_height, 
                element["isIconLabeled"], element["width"], element["height"]
            )
            if recognition_results:
                recognition_feedback_list.append({
                    "element_id": element["id"],
                    "element_name": element["name"],
                    "element_type": element["type"],
                    "Feedback": recognition_results,
                })

        # Prepare feedback data
        feedback_data = {
            "error_prevention_results": self._format_error_prevention_feedback(error_prevention_results),
            "consistency_results": self._format_consistency_feedback(consistency_results),
            "error_handling_results": self._format_error_handling_feedback(error_handling_results),
            "minimalist_results": self._format_minimalist_feedback(minimalist_results),
            "recognition_results": recognition_feedback_list,
            "last_updated": datetime.now(),
            "elements_hash": self._generate_elements_hash(elements)
        }

        # Save feedback to database
        update_result = self.feedback_repository.update_feedback(
            design_name, frame_name, feedback_data
        )

        if update_result.matched_count == 0:
            print("Error updating feedback in MongoDB.")
            return jsonify({"error": "Failed to update feedback in database"}), 500

        print("New feedback processed and saved successfully.")
        return self._format_response(feedback_data), 200

    def _format_error_prevention_feedback(self, results):
        return {
            "ErrorPreventionScore": f"Error Prevention Score: {results.get('ErrorPreventionScore', 0)}%.",
            "ValidationIssues": results.get("ValidationIssues", []),
            "ConfirmationIssues": results.get("ConfirmationIssues", []),
            "Feedback": results.get("Feedback", {})
        }

    def _format_consistency_feedback(self, results):
        return {
            "ColorConsistency": f"Color consistency is {results.get('ColorConsistency', 0)}%.",
            "AlignmentConsistency": f"Alignment consistency is {results.get('AlignmentConsistency', 0)}%.",
            "SizeProportionality": f"Size proportionality is {results.get('SizeProportionality', 0)}%.",
            "Feedback": results.get('Feedback', {})
        }

    def _format_error_handling_feedback(self, results):
        return {
            "ErrorHandlingScore": f"Error Handling Score: {results.get('ErrorHandlingScore', 0)}%.",
            "ErrorIssues": results.get("ErrorIssues", []),
            "RecoveryIssues": results.get("RecoveryIssues", []),
            "Feedback": results.get("Feedback", {})
        }

    def _format_minimalist_feedback(self, results):
        if isinstance(results, tuple):  # Handle case where score is returned separately
            results, _ = results

        cleaned_feedback = []
        if isinstance(results, dict):
            for key, value in results.items():
                cleaned_key = clean_prefix(key)
                issue = self._determine_minimalist_issue(cleaned_key)
                cleaned_feedback.append({
                    "issue": issue,
                    "feedback": clean_prefix(value) if isinstance(value, str) else str(value)
                })
        elif isinstance(results, list):
            for item in results:
                if isinstance(item, str):
                    cleaned_item = clean_prefix(item)
                    issue = self._determine_minimalist_issue(cleaned_item)
                    cleaned_feedback.append({"issue": issue, "feedback": cleaned_item})
                elif isinstance(item, dict):
                    cleaned_feedback.append({
                        "issue": clean_prefix(item.get('issue', '')),
                        "feedback": clean_prefix(item.get('feedback', '')) if isinstance(item.get('feedback'), str) else str(item.get('feedback', ''))
                    })
        
        return {"Feedback": cleaned_feedback}

    def _determine_minimalist_issue(self, text):
        text_lower = text.lower()
        if "white space" in text_lower:
            return "White Space Ratio"
        elif "elements" in text_lower and "irrelevant" not in text_lower:
            return "Number of Elements"
        elif "irrelevant" in text_lower:
            return "Irrelevant Elements"
        elif "score" in text_lower:
            return "Score"
        return text

    def _generate_elements_hash(self, elements):
        """Generate a simple hash to detect if elements have changed"""
        import hashlib
        elements_str = str(sorted([(e['id']), e.get('name', ''), e.get('type', '')] for e in elements))
        return hashlib.md5(elements_str.encode()).hexdigest()

    def _format_cached_response(self, feedback_data):
        """Format cached feedback into standard response format"""
        return jsonify({
            "message": "Returning cached feedback",
            "status": 200,
            "error_prevention_results": feedback_data.get("error_prevention_results", {}),
            "consistency_results": feedback_data.get("consistency_results", {}),
            "error_handling_results": feedback_data.get("error_handling_results", {}),
            "minimalist_results": feedback_data.get("minimalist_results", {}),
            "recognition_results": feedback_data.get("recognition_results", [])
        }), 200

    def _format_response(self, feedback_data):
        """Format new feedback into standard response format"""
        return jsonify({
            "message": "Design processed successfully!",
            "status": 200,
            "error_prevention_results": feedback_data.get("error_prevention_results", {}),
            "consistency_results": feedback_data.get("consistency_results", {}),
            "error_handling_results": feedback_data.get("error_handling_results", {}),
            "minimalist_results": feedback_data.get("minimalist_results", {}),
            "recognition_results": feedback_data.get("recognition_results", [])
        })