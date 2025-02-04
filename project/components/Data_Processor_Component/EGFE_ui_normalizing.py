import json
import pandas as pd
# from sklearn.calibration import LabelEncoder
from sklearn.preprocessing import LabelEncoder

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
            df = pd.get_dummies(df, columns=['type'], prefix='type')  # One-hot encode the 'type' column
            df = df.astype({col: 'int' for col in df.columns if col.startswith('type_')})  # Convert Boolean columns to 0 and 1 
        print("normalized data")
        return df 
 
    def normalize_screen_size(self, screen_size):
        # Manual Normalization
        max_width = 1920  # Standard max screen width
        max_height = 3840  # Standard max screen height

        normalized_width = screen_size['screen_width'] / max_width
        normalized_height = screen_size['screen_height'] / max_height

        return normalized_width, normalized_height
        
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
        
        print("normalized elements and screen size : ")
        return normalized_elements, normalized_screen_size

