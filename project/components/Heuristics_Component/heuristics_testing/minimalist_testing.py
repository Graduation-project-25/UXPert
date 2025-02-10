import json
import os
from components.Heuristics_Component.heuristics_evaluation.evaluation_results import EvaluationResults
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Heuristics_Component.heuristics_testing.heuristic_testing import HeuristicTestingInterface

class MinimalistTesting(HeuristicTestingInterface):    
    def __init__(self):
        self.evaluation_results = EvaluationResults()
        self.minimalist_instance = HeuristicFactory.check_rule("minimalist")

    def evaluate_rule_test(self, test_folder, evaluation_folder):
        data_to_save = {}

        # Evaluate Test Data
        for file_name in os.listdir(test_folder):
            file_path = os.path.join(test_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                feedback = self.minimalist_instance.evaluate_rule(
                    data, data['screen_size']['screen_width'], data['screen_size']['screen_height']
                )
                # Store evaluation results for test data
                result_data = {
                    "screen_size": data["screen_size"],
                    "evaluation": feedback,
                }
                design_id = file_name.split('.')[0]  # Extract design ID
                if design_id not in data_to_save:
                    data_to_save[design_id] = []
                data_to_save[design_id].append(result_data)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")
        
        # Save the results for both training and test data
        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder,"minimalist_test_evaluation.json")

    def analyze_test_results(self, train_json, test_json):
        try:
            with open(train_json, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing training data: {e}. Skipping file.")
            return

        try:
            with open(test_json, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing test data: {e}. Skipping file.")
            return

        training_results = {"Pass": 0, "Fail": 0}
        test_results = {"Pass": 0, "Fail": 0}

        pass_message = "minimalist"

        TP = 0      # True Positive
        FP = 0      # False Positive
        FN = 0      # False Negative

        # Process test data
        for test_design_id, test_designs in test_data.items():
            for test in test_designs:
                predicted_pass = self.is_minimalist_pass(test['evaluation'], pass_message)

                # Assume ground truth is stored in the test data (you might need a real dataset)
                actual_pass = test.get('ground_truth') == "Pass"  # You need a way to define this

                if predicted_pass and actual_pass:
                    TP += 1  # True Positive
                elif predicted_pass and not actual_pass:
                    FP += 1  # False Positive
                elif not predicted_pass and actual_pass:
                    FN += 1  # False Negative

        # Compute Precision, Recall, and F1-Score
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1 Score: {f1_score:.2f}")


    # Helper function to check if "minimalist" exists in the evaluation list
    def is_minimalist_pass(self,evaluation_list,pass_message):
        return any(pass_message.lower() in eval_item.lower() for eval_item in evaluation_list)

