import json
import os
from components.Heuristics_Component.heuristics_evaluation.evaluation_results import EvaluationResults
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory

class MinimalistEvaluation(HeuristicEvaluationInterface):    
    def __init__(self):
        self.evaluation_results = EvaluationResults() 

    def evaluate_rule(self, train_folder, evaluation_folder):
        minimalist_instance = HeuristicFactory.check_rule("minimalist")
        data_to_save = {}
        all_feedback = []  # Store all feedback messages

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract screen size
                screen_width = data['screen_size']['screen_width']
                screen_height = data['screen_size']['screen_height']

                # Evaluate rule
                feedback, score = minimalist_instance.evaluate_rule(data, screen_width, screen_height)

                # Store elements with their evaluation
                result_data = {
                    "screen_size": data["screen_size"],
                    "evaluation": {
                        "feedback": feedback,
                        "score": score
                    }
                }

                # Group by design_id
                design_id = file_name.split('.')[0]  # Remove the file extension to use as the key
                if design_id not in data_to_save:
                    data_to_save[design_id] = []  # Initialize list for this design_id
                data_to_save[design_id].append(result_data)

                # Store feedback messages
                all_feedback.extend(feedback)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")

        # Save evaluation results
        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder, "minimalist_evaluation.json")

        # Print feedback for all processed files
        print(all_feedback)

        return all_feedback  # Return all feedback messages
