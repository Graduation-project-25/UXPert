import json
import os
import pandas as pd

from components.Data_Processor_Component.ui_processor import UiProcessorInterface
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Data_Processor_Component.EGFE_size_estimation import EGFE_SizeEstimation


class EGFE_UiProcessing(UiProcessorInterface):
    def __init__(self):
        self.egfe_ui_extraction = EGFE_FeatureExtraction()
        self.egfe_size_estimation = EGFE_SizeEstimation()
    
    def save_ui_elements(self, elements, image_name, output_path):
        """Saves the extracted UI elements along with screen size to a JSON file."""
        estimated_screen_width, estimated_screen_height = self.egfe_size_estimation.estimate_screen_size(image_name, elements) 
        data_to_save = {
            "screen_size": {"screen_width": estimated_screen_width , "screen_height": estimated_screen_height },
            "elements": elements
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def process_ui_elements(self, json_folder, output_folder):
        """Processes UI JSON files, extracts elements, estimates screen size, and saves the results."""
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

        for json_file in json_files:
            json_file_path = os.path.join(json_folder, json_file)
            output_path = os.path.join(output_folder, json_file)

            try: 
                image_name = os.path.splitext(json_file)[0]

                # Extract UI elements
                ui_elements = self.egfe_ui_extraction.extract_ui_elements(json_file_path)

                # Save the extracted elements and screen size
                self.save_ui_elements(ui_elements, image_name, output_path)

            except Exception as e:
                print(f"Error processing {json_file_path}: {e}")

    def aggregate_ui_elements(self, df):
        """Aggregate UI elements by name and compute average position and size."""
        # Ensure that df is a DataFrame and contains necessary columns
        if isinstance(df, pd.DataFrame):
            if 'elements' in df.columns and 'position.x' in df.columns and 'position.y' in df.columns and 'width' in df.columns and 'height' in df.columns:
                aggregated = df.groupby('elements').agg({
                    'position.x': 'mean',
                    'position.y': 'mean',
                    'width': 'mean',
                    'height': 'mean'
                }).reset_index()
                print("aggregated elements :")
                return aggregated
            else:
                raise ValueError("Missing necessary columns in the DataFrame.")
        else:
            raise ValueError("Input is not a pandas DataFrame.")


