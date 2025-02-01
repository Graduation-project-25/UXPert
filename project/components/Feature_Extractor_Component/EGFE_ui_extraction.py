import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from components.Feature_Extractor_Component.feature_extractor import FeatureExtractorInterface

class EGFE_FeatureExtraction(FeatureExtractorInterface):
    
    def extract_json_file_path(self, json_folder, limit=50):
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')][:limit]
        index =0
        if index >= len(json_files):
            index = 0
        json_file_path = os.path.join(json_folder, json_files[index])
        return json_file_path

    def extract_ui_elements(self, json_file_path):
        """Extracts UI elements from a given JSON file."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        elements = []
        for layer in data.get('layers', []):
            rect = layer.get('rect', {})
            element = {
                'type': layer.get('_class', ''),
                'position': {
                    'x': rect.get('x', 0),
                    'y': rect.get('y', 0)
                },
                'width': rect.get('width', 0),
                'height': rect.get('height', 0),
                'name': layer.get('name', ''),  # Using 'name' as the text/label
                'color': layer.get('color', '')
            }
            elements.append(element)
        #print (elements)
        #print("Extracted Elements:\n", json.dumps(elements, indent=4))

        # Normalize json data into a flat table
        df = pd.json_normalize(elements)

        # Normalize into scaled data 
        normalized_data = self.normalize_ui_elements(elements, df)
        # print("Normalized, Scaled Data:\n", normalized_data)
        # print("***************************************************************\n")    

        return elements, normalized_data

    def save_ui_elements(self, elements, screen_size, output_path):
        """Saves the extracted UI elements along with screen size to a JSON file."""
        data_to_save = {
            "screen_size": {"width": screen_size[0], "height": screen_size[1]},
            "elements": elements
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

        print(f"Saved extracted elements and screen size to: {output_path}")


    def estimate_screen_size(self, design_json):
        """Estimates the screen size based on UI elements' positions and dimensions."""
        max_x = max_y = 0

        for element in design_json.get("elements", []):
            x, y = element.get("x", 0), element.get("y", 0)
            width, height = element.get("width", 0), element.get("height", 0)

            max_x = max(max_x, x + width)
            max_y = max(max_y, y + height)

        return int(max_x), int(max_y)  # Return estimated width and height


    def process_ui_elements(self, json_folder, image_folder, output_folder):
        """Processes UI JSON files, extracts elements, estimates screen size, and saves the results."""
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

        for json_file in json_files:
            json_file_path = os.path.join(json_folder, json_file)
            output_path = os.path.join(output_folder, json_file)

            try:
                print(f"Processing: {json_file_path}")

                # Load the JSON data
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    design_json = json.load(f)

                # Extract UI elements
                ui_elements, normalized_data = self.extract_ui_elements(json_file_path)

                # Estimate screen size
                screen_size = self.estimate_screen_size(design_json)
                
                # Save the extracted elements and screen size
                self.save_ui_elements(ui_elements, screen_size, output_path)

            except Exception as e:
                print(f"Error processing {json_file_path}: {e}")

    def normalize_ui_elements(self, elements, df):
        # Scaling width, height, position.x, position.y
        scale = MinMaxScaler()
        X = df[['width', 'height', 'position.x', 'position.y']]
        df[['width', 'height', 'position.x', 'position.y']] = scale.fit_transform(X)
        
        # Extract RGBA values and one-hot encode the 'type' column
        df[['color_r', 'color_g', 'color_b', 'color_a']] = pd.DataFrame(df['color'].tolist(), index=df.index) # RGBA
        df = pd.get_dummies(df, columns=['type'], prefix='type') # One-hot encode the 'type' column
        df = df.astype({col: 'int' for col in df.columns if col.startswith('type_')}) # Convert Boolean columns to 0 and 1
        return df

    def aggregate_ui_elements(self, df):
        """Aggregate UI elements by name and compute average position and size."""
        aggregated = df.groupby('name').agg({
            'position.x': 'mean',
            'position.y': 'mean',
            'width': 'mean',
            'height': 'mean'
        }).reset_index()
        return aggregated

    def split_dataset(self, df):
        """Splits the dataset into training and testing sets."""
        X=df
        X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
        return X_train, X_test