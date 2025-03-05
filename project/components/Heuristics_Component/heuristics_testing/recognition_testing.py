import json
import os
from components.Heuristics_Component.heuristics_evaluation.evaluation_results import EvaluationResults
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory
from components.Heuristics_Component.heuristics_testing.heuristic_testing import HeuristicTestingInterface
from components.Heuristics_Component.heuristic_rules.recognition import Recognition

class RecognitionTesting(HeuristicTestingInterface):
    def __init__(self):
        self.evaluation_results = EvaluationResults()
        self.recognition_instance = HeuristicFactory.check_rule("recognition")
        self.rule = Recognition()

    def evaluate_rule_test(self, test_folder, evaluation_folder):
        data_to_save = {}

        for file_name in os.listdir(test_folder):
            file_path = os.path.join(test_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                design_id = file_name.split('.')[0]  # Extract design ID

                if design_id not in data_to_save:
                    data_to_save[design_id] = []

                for element in data['elements']:
                    screen_width = data['screen_size']['screen_width']
                    screen_height = data['screen_size']['screen_height']

                    element_type = None
                    for k, v in element.items():
                        if k.startswith("type_") and v == 1:
                            element_type = k.replace("type_", "")
                            break

                    icon_width = element.get('width', None)
                    icon_height = element.get('height', None)
                    labeled = element.get('labeled', None)

                    is_icon = element_type == "symbolInstance"

                    is_icon_labeled = False
                    if is_icon and 'labeled' in element:
                        is_icon_labeled = element['labeled'] == True or element['labeled'] == 1

                    feedback = self.rule.evaluate_rule(
                        element, element_type, screen_width, screen_height, is_icon_labeled, icon_width, icon_height
                    )

                    result_data = {
                        "element": element,
                        "evaluation": feedback,
                    }
                    data_to_save[design_id].append(result_data)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")

        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder, "recognition_test_evaluation.json")

    def analyze_test_results(self, train_json, test_json):
        pass