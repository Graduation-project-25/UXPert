import json
import os

import pandas as pd
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.heuristic_factory import HeuristicFactory

class MinimalistEvaluation(HeuristicEvaluationInterface):    
    # def __init__(self):

    def evaluate_rule(self, designs, evaluation_folder):
        self.evaluate_white_space_ratio(designs, evaluation_folder)

    def evaluate_white_space_ratio(self, train_folder, evaluation_folder):
        minimalist_instance = HeuristicFactory.check_rule("minimalist")
        data_to_save = {}

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(file_name)
                white_space_ratio, feedback = minimalist_instance.evaluate_white_space_ratio(data,data['screen_size']['screen_width'],data['screen_size']['screen_height'])
                
                # Store elements with their evaluation
                result_data = {
                    "design_id": file_name,
                    "screen_size": data["screen_size"],
                    # "elements": data["elements"],  # Keeping all elements in the result file
                    "white_space_ratio": white_space_ratio,
                    "evaluation": feedback,
                }

                # Group by design_id
                design_id = file_name.split('.')[0]  # Remove the file extension to use as the key
                if design_id not in data_to_save:
                    data_to_save[design_id] = []  # Initialize list for this design_id
                data_to_save[design_id].append(result_data)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")
        self.save_white_space_ratio_evaluation_result(data_to_save,evaluation_folder)


    def save_white_space_ratio_evaluation_result(self, data_to_save, evaluation_folder):
        """ Saves the evaluation result for each design in a new JSON file """
        os.makedirs(evaluation_folder, exist_ok=True)  # This will create the directory if it doesn't exist

        output_file_path = os.path.join(evaluation_folder, "white_space_evaluation.json")
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            json.dump(data_to_save, out_file, indent=4, ensure_ascii=False)
