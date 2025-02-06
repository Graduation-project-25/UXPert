import json
import os


class EvaluationResults():    
    def save_white_space_ratio_evaluation_result(self, data_to_save, evaluation_folder, file_name):
        """ Saves the evaluation result for each design in a new JSON file """
        os.makedirs(evaluation_folder, exist_ok=True)  # This will create the directory if it doesn't exist

        output_file_path = os.path.join(evaluation_folder, file_name)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            json.dump(data_to_save, out_file, indent=4, ensure_ascii=False)

