import json
import os
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory

class MinimalistEvaluation(HeuristicEvaluationInterface):    
    # def __init__(self):

    def evaluate_rule(self, designs):
        self.evaluate_white_space_ratio(designs)

    def evaluate_white_space_ratio(self, train_folder):
        minimalist_instance = HeuristicFactory.check_rule("minimalist")

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(file_name)
                white_space_ratio, feedback = minimalist_instance.evaluate_minimalist(data,data['screen_size']['screen_width'],data['screen_size']['screen_height'])
                # print(feedback)
                # Store elements with their evaluation
                # result_data = {
                #     "design_id": file_name,
                #     "screen_size": data["screen_size"],
                #     "white_space_ratio": white_space_ratio,
                #     "evaluation": feedback,
                #     "elements": data["elements"]  # Keeping all elements in the result file
                # }
                # Save result in a new JSON file
                # self.save_white_space_ratio_evaluation_result(file_name, result_data, output_folder)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")

    def save_white_space_ratio_evaluation_result(self, file_name, result_data, output_folder):
        """ Saves the evaluation result for each design in a new JSON file """

        output_path = os.path.join(output_folder, f"evaluated_{file_name}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=4)

        print(f"Evaluation results saved to {output_path}")
