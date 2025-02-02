import json
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from components.Data_Processor_Component.ui_normalizer import UiNormalizerInterface
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction


class EGFE_UiNormalizing(UiNormalizerInterface):
    def __init__(self):
        self.scale = MinMaxScaler()
        self.egfe_ui_extraction = EGFE_FeatureExtraction()

    def normalize_ui_elements(self, elements):
        # Convert the elements list into a DataFrame for easy processing
        # df = pd.DataFrame(elements)
        df = pd.json_normalize(elements)

        # Scaling width, height, position.x, position.y
        X = df[['width', 'height', 'position.x', 'position.y']]
        df[['width', 'height', 'position.x', 'position.y']] = self.scale.fit_transform(X)
        
        # Extract RGBA values and one-hot encode the 'type' column
        df[['color_r', 'color_g', 'color_b', 'color_a']] = pd.DataFrame(df['color'].tolist(), index=df.index)  # RGBA
        df = pd.get_dummies(df, columns=['type'], prefix='type')  # One-hot encode the 'type' column
        df = df.astype({col: 'int' for col in df.columns if col.startswith('type_')})  # Convert Boolean columns to 0 and 1
        
        return df 

    def normalize_screen_size(self, screen_size):
        # Ensure screen_size contains 'width' and 'height'
        if 'screen_width' in screen_size and 'screen_height' in screen_size:
            # Create a DataFrame for screen size
            screen_df = pd.DataFrame([screen_size])

            # Normalize the screen size (width, height)
            screen_df[['screen_width', 'screen_height']] = self.scale.fit_transform(screen_df[['screen_width', 'screen_height']])

            return screen_df[['screen_width', 'screen_height']]
        else:
            raise ValueError("Screen size does not contain 'screen_width' and 'screen_height' keys.")

    def get_normalized_data(self, data):

        # Separate screen size and elements
        screen_size = data['screen_size']
        elements = data['elements']

        # Normalize the elements first
        normalized_elements = self.normalize_ui_elements(elements)

        # Normalize the screen size and add it to the DataFrame
        normalized_screen_size = self.normalize_screen_size(screen_size)

        # print(normalized_screen_size)
        # print(screen_size)
        return normalized_elements,normalized_screen_size

    def get_all_normalized_json_files(self,json_folder):
        # Get all JSON file paths from the folder
        json_file_paths = self.egfe_ui_extraction.extract_json_file_paths(json_folder)

        # Initialize an empty list to store the normalized data for all files
        all_normalized_data = []
        all_screen_sizes = []

        for json_file_path in json_file_paths:
            print(f"Processing file: {json_file_path}")
            
            # Read JSON data from the file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Get normalized data
            normalized_elements,normalized_screen_size = self.get_normalized_data(data)
            
            # Add file name to the DataFrame for tracking
            normalized_elements["file_name"] = json_file_path.split("/")[-1]  

            # Append the results to lists
            all_normalized_data.append(normalized_elements)
            all_screen_sizes.append(normalized_screen_size)

            print(normalized_screen_size)
            print(normalized_elements)
            
            print("***************************************************************************")
        if not all_normalized_data:
            raise ValueError("No valid JSON files were found or processed.")

        # Concatenate all DataFrames
        combined_elements_df = pd.concat(all_normalized_data, ignore_index=True)
        combined_screen_sizes_df = pd.concat(all_screen_sizes, ignore_index=True)

        return combined_elements_df, combined_screen_sizes_df
