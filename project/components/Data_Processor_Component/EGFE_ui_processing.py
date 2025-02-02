import json
import os
from PIL import Image
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from components.Data_Processor_Component.ui_processor import UiProcessorInterface
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction


class EGFE_UiProcessing(UiProcessorInterface):
    def __init__(self):
        self.egfe_ui_extraction = EGFE_FeatureExtraction()
    
    # save each extracted element, screen size to extractedFeatures folder
    def save_ui_elements(self, elements,image_name, output_path):
        # print(image_name)
        # """Saves the extracted UI elements along with screen size to a JSON file."""
        width,height = self.estimate_screen_size(image_name)
        data_to_save = {
            "screen_size": {"screen_width": width, "screen_height": height},
            "elements": elements
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

        # print(f"Saved extracted elements and screen size to: {output_path}")

    def estimate_screen_size(self, image_name):
        image_path = f"data/raw/EGFE/images/{image_name}.png"
        try:
            # Load an image
            image = Image.open(image_path)

            # Get the size of the image
            width, height = image.size
        except FileNotFoundError:
            print(f"Warning: Image '{image_name}.png' not found. Returning default size.")
            width, height = 1920, 1080  # Default resolution

        # print(f"The image resolution is: {width}x{height}")
        return width, height

    #save result to ExtractedFeatures Folder
    def process_ui_elements(self, json_folder, output_folder):
        # """Processes UI JSON files, extracts elements, estimates screen size, and saves the results."""
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

        for json_file in json_files:
            json_file_path = os.path.join(json_folder, json_file)
            output_path = os.path.join(output_folder, json_file)

            try:
                # print(f"Processing: {json_file_path}")
                image_name = os.path.splitext(json_file)[0]
                # print(image_name)

                # Extract UI elements
                ui_elements = self.egfe_ui_extraction.extract_ui_elements(json_file_path)                
                # ui_elements, normalized_data = self.egfe_ui_extraction.extract_ui_elements(json_file_path)                
                # Save the extracted elements and screen size
                self.save_ui_elements(ui_elements,image_name, output_path)

            except Exception as e:
                print(f"Error processing {json_file_path}: {e}")

    def aggregate_ui_elements(self, df):
        """Aggregate UI elements by name and compute average position and size."""
        aggregated = df.groupby(df['elements']).agg({
            'position.x': 'mean',
            'position.y': 'mean',
            'width': 'mean',
            'height': 'mean'
        }).reset_index()
        return aggregated



        # Define the function to process all JSON files in a directory
   
    def split_dataset(self, df):
        """Splits the dataset into training and testing sets."""
        X=df
        X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
        return X_train, X_test