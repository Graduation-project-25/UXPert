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
                # print(data)
                # consistent_navigation_feedback = recognition_instance.consistent_navigation(data)
                # visible_instructions_feedback = self.recognition_instance.visible_instructions(data)
                # minimized_memory_load_feedback= self.recognition_instance.minimized_memory_load(data)

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

                    icons = element.get('type_symbolInstance', None)
                    icon_width = element.get('width', None)
                    icon_height = element.get('height', None)
                    labeled = element.get('labeled', None)

                    # is_icon = icons is not None
                    is_icon = icons == 1 # check if the value is 1.
                    is_icon_labeled = labeled is not None if is_icon else False


                    # Call evaluate_rule
                    icon_visibility_feedback = self.recognition_instance.evaluate_rule(element, element_type, screen_width, screen_height, is_icon_labeled, icon_width, icon_height, is_icon)

                    # Save the updated element with feedback
                    # element["Icons evaluation"] = icon_visibility_feedback
                    element["All Feedback"] = icon_visibility_feedback
                    # element["visible instructions"] = self.recognition_instance.visible_instructions(element, element_type)
                    # element["minimized memory load"] = self.recognition_instance.minimized_memory_load(element, element_type, screen_width, screen_height)

                    # Store results per cluster
                    data_to_save[key] = elements

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing: {e}. Skipping file.")
        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder, "recognition_evaluation.json")



