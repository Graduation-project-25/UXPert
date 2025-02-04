import json
import os
import pandas as pd
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Loader_Component.load_data import LoadDataInterface

class EGFE_LoadData(LoadDataInterface):    
    def __init__(self, train_folder):
        self.train_folder = train_folder
        self.egfe_ui_normalizing = EGFE_UiNormalizing()

    def load_train_data(self):
        """Load and merge all JSON files from the training folder into a DataFrame."""
        all_data = []
        
        for file_name in os.listdir(self.train_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.train_folder, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        if "elements" not in data:
                            print(f"Warning: 'elements' key missing in {file_name}. Skipping file.")
                            continue

                        df = self.egfe_ui_normalizing.normalize_ui_elements(data["elements"])
                        df['screen_width'],df["screen_height"] = self.egfe_ui_normalizing.normalize_screen_size(data["screen_size"])
                        df["file_name"] = file_name  # Track the file source

                        all_data.append(df)

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing {file_name}: {e}. Skipping file.")

        if not all_data:
            raise ValueError("No JSON files found in the training folder.")
        
        return pd.concat(all_data, ignore_index=True)
    

