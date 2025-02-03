import json
import pandas as pd
from sklearn.calibration import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

from components.Data_Processor_Component.ui_normalizer import UiNormalizerInterface
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction

class EGFE_UiNormalizing(UiNormalizerInterface):
    def __init__(self):
        self.scale = MinMaxScaler()
        self.egfe_ui_extraction = EGFE_FeatureExtraction()

    def normalize_ui_elements(self, elements):
        # Convert the elements list into a DataFrame for easy processing
        df = pd.json_normalize(elements)

        # Scaling width, height, position.x, position.y
        X = df[['width', 'height', 'position.x', 'position.y']]
        df[['width', 'height', 'position.x', 'position.y']] = self.scale.fit_transform(X)
        
        # Extract RGBA values and one-hot encode the 'type' column
        if "color" in df.columns:
            df[['color_r', 'color_g', 'color_b', 'color_a']] = pd.DataFrame(df['color'].tolist(), index=df.index)  # RGBA


        if "type" in df.columns:
            df = pd.get_dummies(df, columns=['type'], prefix='type')  # One-hot encode 'type' column
            df = df.astype({col: 'int' for col in df.columns if col.startswith('type_')})  # Convert to 0 and 1 

        return df 

    def normalize_screen_size(self, screen_size):
        # Manual Normalization
        max_width = 1920  # Standard max screen width
        max_height = 3840  # Standard max screen height

        normalized_width = screen_size['screen_width'] / max_width
        normalized_height = screen_size['screen_height'] / max_height

        return {"screen_width": normalized_width, "screen_height": normalized_height}
        
        # Another way: MinMaxScaler 
        # sample_sizes = pd.DataFrame([
        #     {"screen_width": 800, "screen_height": 1280},
        #     {"screen_width": 1440, "screen_height": 2560},
        #     {"screen_width": 1920, "screen_height": 3840}
        # ])
        
        # # Fit on multiple values
        # self.scale.fit(sample_sizes)  
        # screen_df = pd.DataFrame([screen_size])
        # screen_df[['screen_width', 'screen_height']] = self.scale.transform(screen_df[['screen_width', 'screen_height']])
        
        # return screen_df[['screen_width', 'screen_height']].to_dict(orient='records')[0]

    def get_normalized_data(self, data):
        # Access screen_size from the new structure
        if 'screen_size' not in data or 'screen_width' not in data['screen_size'] or 'screen_height' not in data['screen_size']:
            raise KeyError("The dataset does not contain 'screen_width' or 'screen_height'. Check JSON structure.")
        
        # Update to access screen_size values correctly
        screen_size = {"screen_width": data['screen_size']['screen_width'], "screen_height": data['screen_size']['screen_height']}
        elements = data['elements']

        # Normalize the elements first
        normalized_elements = self.normalize_ui_elements(elements)
        
        # Normalize the screen size and return
        normalized_screen_size = self.normalize_screen_size(screen_size)

        return normalized_elements, normalized_screen_size

