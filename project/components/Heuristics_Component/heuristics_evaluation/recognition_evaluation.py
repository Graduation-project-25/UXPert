import json
from components.Heuristics_Component.heuristics_evaluation.evaluation_results import EvaluationResults
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory

class RecognitionEvaluation(HeuristicEvaluationInterface):    
    def __init__(self):
        self.evaluation_results = EvaluationResults()
        self.recognition_instance = HeuristicFactory.check_rule("recognition")

 
    def evaluate_rule(self, clustered_data, evaluation_folder):
        data_to_save = {}

        try:
            with open(clustered_data, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, elements in data.items():
                for element in elements:
                    screen_width = element.get("screen_width", 1920)
                    screen_height = element.get("screen_height", 1080)

                    # Determine element type
                    element_type = None
                    for k, v in element.items():
                        if k.startswith("type_") and v == 1:
                            element_type = k.replace("type_", "")
                            break

                    icon_width = element.get('width', None)
                    icon_height = element.get('height', None)
                    labeled = element.get('labeled', None)

                    # Determine if it's an icon
                    is_icon = element_type == "symbolInstance"

                    # Robust labeled detection
                    is_icon_labeled = False
                    if is_icon and 'labeled' in element:
                        is_icon_labeled = element['labeled'] == True or element['labeled'] == 1

                    all_feedback = self.recognition_instance.evaluate_rule(element, element_type, screen_width, screen_height, is_icon_labeled, icon_width, icon_height)
                    element["All Feedback"] = all_feedback
                    print(all_feedback)

                data_to_save[key] = elements

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing: {e}. Skipping file.")

        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder, "recognition_evaluation.json")



