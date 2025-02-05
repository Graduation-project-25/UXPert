import json
import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Loader_Component.load_data import LoadDataInterface

class EGFE_LoadData(LoadDataInterface):    
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.egfe_ui_normalizing = EGFE_UiNormalizing()

    def load_data(self):
        """Load and merge all JSON files from the data folder into a DataFrame."""
        all_data = []
        # max_num, min_num = self.get_max_min_file_name()
        
        for file_name in os.listdir(self.data_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.data_folder, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        if "elements" not in data:
                            print(f"Warning: 'elements' key missing in {file_name}. Skipping file.")
                            continue

                        # file_name = os.path.splitext(file_name)[0]
                        # file_name = int(file_name)
                        
                        df = self.egfe_ui_normalizing.normalize_ui_elements(data["elements"])
                        df['screen_width'],df["screen_height"] = self.egfe_ui_normalizing.normalize_screen_size(data["screen_size"])
                        # df["file_name"]  = (file_name-min_num)/(max_num-min_num)

                        all_data.append(df)

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing {file_name}: {e}. Skipping file.")

        if not all_data:
            raise ValueError("No JSON files found in the data folder.")
        
        return pd.concat(all_data, ignore_index=True)
    

    # def get_max_min_file_name(self):
    #     file_names = []
    #     for file_name in os.listdir(self.data_folder):
    #         if file_name.endswith(".json"):
    #             file_name = os.path.splitext(file_name)[0]
    #             file_name = int(file_name)
    #             file_names.append(file_name)
    #     return max(file_names), min(file_names)
        

                

