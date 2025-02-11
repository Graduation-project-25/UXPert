import json
import os
from ..heuristics_evaluation.evaluation_results import EvaluationResults
from ..heuristic_rules.heuristic_factory import HeuristicFactory
from ..heuristics_testing.heuristic_testing import HeuristicTestingInterface
from ..heuristic_rules.minimalist import Minimalist

class MinimalistTesting(HeuristicTestingInterface):    
    def __init__(self):
        self.evaluation_results = EvaluationResults()
        self.minimalist_instance = HeuristicFactory.check_rule("minimalist")
        self.rule = Minimalist()

    def evaluate_rule_test(self, test_folder, evaluation_folder):
        data_to_save = {}

        # Evaluate Test Data
        for file_name in os.listdir(test_folder):
            file_path = os.path.join(test_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Ensure required keys exist before processing
                if not isinstance(data, dict) or 'screen_size' not in data or 'elements' not in data:
                    print(f"Skipping invalid test data in {file_name}: Missing required keys")
                    continue
                
                feedback = self.rule.evaluate_rule(
                    data['elements'], data['screen_size']['screen_width'], data['screen_size']['screen_height']
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
        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder, "minimalist_test_evaluation.json")

    def analyze_test_results(self, train_folder, test_folder):
        train_files = [os.path.join(train_folder, f) for f in os.listdir(train_folder) if f.endswith('.json')]
        test_files = [os.path.join(test_folder, f) for f in os.listdir(test_folder) if f.endswith('.json')]

        training_data = {}
        test_data = {}

        # Load training data
        for train_file in train_files:
            try:
                with open(train_file, 'r', encoding='utf-8') as f:
                    training_data.update(json.load(f))
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error processing {train_file}: {e}. Skipping file.")

        # Load test data with additional validation
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):  # If JSON root is a list, use file name as key
                        test_data[test_file] = data
                    elif isinstance(data, dict):
                        test_data.update(data)
                    else:
                        print(f"Skipping {test_file}: Unexpected data format")
                        continue
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error processing {test_file}: {e}. Skipping file.")

        TP = FP = TN = FN = 0  # Initialize counters
        total_samples = 0  # Count total test samples
        pass_threshold = 70  # Define threshold for passing

        # Process test data
        for test_design_id, test_designs in test_data.items():
            for test in test_designs:
                print("Type of test:", type(test))  # Debugging output
                print("Raw test data:", test)

                if not isinstance(test, dict) or 'elements' not in test or 'screen_width' not in test or 'screen_height' not in test:
                    print(f"Skipping invalid test data: {test}")
                    continue  # Skip this test case
                
                feedback, score = self.rule.evaluate_rule(test['elements'], test['screen_width'], test['screen_height'])
                print("Score:", score)
                predicted_pass = (score >= pass_threshold)

                # Extract ground truth from the test data (modify as needed)
                actual_pass = test.get('ground_truth', 0) >= pass_threshold  # Default to "Fail" if missing

                if predicted_pass and actual_pass:
                    TP += 1  # True Positive
                elif predicted_pass and not actual_pass:
                    FP += 1  # False Positive
                elif not predicted_pass and actual_pass:
                    FN += 1  # False Negative
                else:
                    TN += 1  # True Negative

                total_samples += 1

        # Compute Accuracy, Precision, Recall, and F1-Score
        accuracy = (TP + TN) / total_samples if total_samples > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        print(f"Accuracy: {accuracy:.2f}")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1 Score: {f1_score:.2f}")


    # Helper function to check if "minimalist" exists in the evaluation list
    def is_minimalist_pass(self, evaluation_list, pass_message):
        return any(pass_message.lower() in eval_item.lower() for eval_item in evaluation_list)

