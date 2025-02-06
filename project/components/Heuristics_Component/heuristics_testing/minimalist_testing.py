import json
import os
from components.Heuristics_Component.heuristics_evaluation.evaluation_results import EvaluationResults
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Heuristics_Component.heuristics_testing.heuristic_testing import HeuristicTestingInterface

class MinimalistTesting(HeuristicTestingInterface):    
    def __init__(self):
        self.evaluation_results = EvaluationResults()

    def evaluate_rule_test(self, designs, evaluation_folder):
        self.evaluate_white_space_ratio_test(designs, evaluation_folder)
    def evaluate_white_space_ratio_test(self, test_folder, evaluation_folder):
        minimalist_instance = HeuristicFactory.check_rule("minimalist")
        data_to_save = {}

        # Evaluate Test Data
        for file_name in os.listdir(test_folder):
            file_path = os.path.join(test_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                white_space_ratio, feedback = minimalist_instance.evaluate_white_space_ratio(
                    data, data['screen_size']['screen_width'], data['screen_size']['screen_height']
                )

                # Store evaluation results for test data
                result_data = {
                    "screen_size": data["screen_size"],
                    "white_space_ratio": white_space_ratio,
                    "evaluation": feedback,
                }

                design_id = file_name.split('.')[0]  # Extract design ID
                if design_id not in data_to_save:
                    data_to_save[design_id] = []
                data_to_save[design_id].append(result_data)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")
        
        # Save the results for both training and test data
        self.evaluation_results.save_white_space_ratio_evaluation_result(data_to_save, evaluation_folder,"white_space_test_evaluation.json")

    def analyze_results(self):
        try:
            with open('./data/raw/EGFE/extractedFeatures/evaluation/white_space_evaluation.json', 'r', encoding='utf-8') as f:
                training_data = json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing: {e}. Skipping file.")
        try:
            with open('./data/raw/EGFE/extractedFeatures/evaluation/white_space_test_evaluation.json', 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing: {e}. Skipping file.")

        
        training_results = { "Pass": 0, "Fail": 0 }
        test_results = { "Pass": 0, "Fail": 0 }
        pass_minimalist = 'Minimalist Design'

        for train_design_id, train_designs in training_data.items():
            for train in train_designs:
                if train['evaluation'].lower() == pass_minimalist.lower():
                    training_results["Pass"] += 1
                else:
                    training_results["Fail"] += 1

        for test_design_id, test_designs in test_data.items():
            for test in test_designs:
                if test['evaluation'].lower() == pass_minimalist.lower():
                    test_results["Pass"] += 1
                else:
                    test_results["Fail"] += 1


        train_pass_result = training_results['Pass']
        train_fail_result = training_results['Fail']
        test_pass_result = test_results['Pass']
        test_fail_result = test_results['Fail']


        total_train = train_pass_result + train_fail_result
        total_test = test_pass_result + test_fail_result

        accuracy_train = (train_pass_result / total_train) * 100  # Pass in training data
        accuracy_test = (test_pass_result / total_test) * 100  # Pass in test data

        print(f"Training Pass/Fail: {training_results}")
        print(f"Test Pass/Fail: {test_results}")
        print(f"accuracy_train: {accuracy_train}")
        print(f"accuracy_test: {accuracy_test}")
