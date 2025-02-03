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


    def clean_data(self, df):
        print("Checking for missing values...")
        missing_values = df.isnull().sum().sum()
        if missing_values > 0:
            print(f"Found {missing_values} missing values. Cleaning data...")
            df = df.fillna(0, inplace=True)  # Replace NaN with 0 (or use another strategy)
        else:
            print("No missing values found.")
        return df

    
    def save_ui_elements(self, elements, image_name, output_path):
        """Saves the extracted UI elements along with screen size to a JSON file."""
        width, height = self.estimate_screen_size(image_name)
        data_to_save = {
            "screen_size": {"screen_width": width, "screen_height": height},
            "elements": elements
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

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

        return width, height

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

                return aggregated
            else:
                raise ValueError("Missing necessary columns in the DataFrame.")
        else:
            raise ValueError("Input is not a pandas DataFrame.")

    def convert_json_to_dataframe(self, json_folder):
        """Helper method to convert JSON files to a pandas DataFrame."""
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
        all_elements = []

        for json_file in json_files:
            json_file_path = os.path.join(json_folder, json_file)
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for element in data.get("elements", []):
                    element_data = {
                        'elements': element.get('name', ''),
                        'position.x': element.get('position', {}).get('x', 0),
                        'position.y': element.get('position', {}).get('y', 0),
                        'width': element.get('size', {}).get('width', 0),
                        'height': element.get('size', {}).get('height', 0)
                    }
                    all_elements.append(element_data)

        # Convert the list of dictionaries into a pandas DataFrame
        df = pd.DataFrame(all_elements)
        return df
