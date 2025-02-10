import json
from components.Heuristics_Component.heuristics_evaluation.evaluation_results import EvaluationResults
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory

class RecognitionEvaluation(HeuristicEvaluationInterface):    
    def __init__(self):
        self.evaluation_results = EvaluationResults()


    def evaluate_rule(self, clustered_data, evaluation_folder):
        recognition_instance = HeuristicFactory.check_rule("recognition")
        data_to_save = {}
        try:
            with open(clustered_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # print(data)
                consistent_navigation_feedback = recognition_instance.consistent_navigation(data)
                visible_instructions_feedback = recognition_instance.visible_instructions(data)
                minimized_memory_load_feedback= recognition_instance.minimized_memory_load(data)

            for key, elements in data.items():
                for element in elements:  
                    icons = element.get('type_symbolInstance', None)
                    icon_width = element.get('width', None)
                    icon_height = element.get('height', None)
                    labeled = element.get('labeled', None)

                    if icons:
                        if labeled:
                            is_icon_labeled = True
                        else: is_icon_labeled = False
                        icon_visibility_feedback = recognition_instance.evaluate_rule(is_icon_labeled,icon_width,icon_height)

                    else: break

                    # Save the updated element with feedback
                    element["Icons evaluation"] = icon_visibility_feedback  
                element["consistent navigation"] = consistent_navigation_feedback  
                element["visible instructions"] = visible_instructions_feedback  
                element["minimized memory load"] = minimized_memory_load_feedback  

                # Store results per cluster
                data_to_save[key] = elements  

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing: {e}. Skipping file.")
        self.evaluation_results.save_evaluation_result(data_to_save, evaluation_folder, "recognition_evaluation.json")

            

