import pandas as pd
from flask import jsonify, request
from components.Heuristics_Component.heuristic_factory import HeuristicFactory
from components.Suggestions_Component.suggestions import Suggestions
from database.feedback_repository import FeedbackRepository
from components.Suggestions_Component.suggestions import Suggestions
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository
from utils.helpers import clean_prefix

class Feedback:
    def __init__(self):
        self.figma_repository = FigmaFeaturesRepository()
        self.suggestions_repository = SuggestionsRepository()
        self.feedback_repository = FeedbackRepository()

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

        elements_df = pd.DataFrame(elements)

        try:
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
            self.suggestions_repository.save_original_image_id(feature_data)

            # 3. Get the image FROM THE CORRECT REPOSITORY
            frame_image = self.figma_repository.get_image_by_frame_id(
                feature_data["design_name"],
                feature_data["frame_id"]
            )
            print("Data inserted successfully.")
            # if frame_image:
            #     suggestions = Suggestions(frame_image)
            #     suggestions.generate_suggestions()

            # if insert_result.matched_count > 0:
            #     print(f"Frame added to existing design: {design_name}")
            # else:
            #     print(f"New design document created: {design_name}")

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
            minimalist_results, minimalist_score = minimalist_evaluator.evaluate_rule({"elements": elements}, screen_width, screen_height)
            error_handling_results = error_handling_evaluator.evaluate_rule(elements_df)
            error_prevention_results = error_prevention_evaluator.evaluate_rule(elements_db)
            for element in elements:
                recognition_results = recognition_evaluator.evaluate_rule(element, element["type"], screen_width, screen_height, element["isIconLabeled"], element["width"], element["height"])
                if recognition_results:
                    recognition_feedback = {
                        "element_id": element["id"],
                        "element_name": element["name"],
                        "element_type": element["type"],
                        "Feedback": recognition_results,
                    }
                    recognition_feedback_list.append(recognition_feedback)

            # Transform minimalist results
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
                for i, item in enumerate(minimalist_results):
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

            # Prepare human-readable feedback
            consistency_feedback = {
                "ColorConsistency": f"Color consistency is {consistency_results.get('ColorConsistency', 0)}%.",
                "AlignmentConsistency": f"Alignment consistency is {consistency_results.get('AlignmentConsistency', 0)}%.",
                "SizeProportionality": f"Size proportionality is {consistency_results.get('SizeProportionality', 0)}%.",
                "Feedback": consistency_results.get('Feedback', {})
            }

            error_feedback = {
                "ErrorPreventionScore": f"Error Prevention Score: {error_prevention_results.get('ErrorPreventionScore', 0)}%.",
                "ValidationIssues": error_prevention_results.get("ValidationIssues", []),
                "ConfirmationIssues": error_prevention_results.get("ConfirmationIssues", []),
                "Feedback": error_prevention_results.get("Feedback", {})
            }

            error_handling_feedback = {
                "ErrorHandlingScore": f"Error Handling Score: {error_handling_results.get('ErrorHandlingScore', 0)}%.",
                "ErrorIssues": error_handling_results.get("ErrorIssues", []),
                "RecoveryIssues": error_handling_results.get("RecoveryIssues", []),
                "Feedback": error_handling_results
            }

            minimalist_feedback = {
                "Feedback": cleaned_minimalist_feedback,
            }

            feedback_data = {
                "error_prevention_results": error_prevention_results,
                "consistency_results": consistency_results,
                "error_handling_results": error_handling_results,
                "minimalist_results": minimalist_feedback,
            }
            if recognition_feedback_list:
                feedback_data["recognition_results"] = recognition_feedback_list

            # Update feedback in database
            update_result = self.feedback_repository.update_feedback(design_name, frame_name, feedback_data)

            if update_result.matched_count == 0:
                print("Error updating feedback in MongoDB.")
                return jsonify({"error": "Failed to update feedback in database"}), 500
            print("Feedback saved successfully.")

            # Prepare final response
            response_data = {
                "message": "Design processed successfully!",
                "status": 200,
                "error_prevention_results": error_feedback,
                "consistency_results": consistency_feedback,
                "error_handling_results": error_handling_feedback,
                "minimalist_results": minimalist_feedback,
            }
            if recognition_feedback_list:
                response_data["recognition_results"] = recognition_feedback_list

            return jsonify(response_data), 200

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500