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
        # Ensure screen_size contains 'width' and 'height'
        if 'screen_width' in screen_size and 'screen_height' in screen_size:
            # Create a DataFrame for screen size
            screen_df = pd.DataFrame([screen_size])

            # Normalize the screen size (width, height)
            
            screen_df[['screen_width', 'screen_height']] = self.scale.fit_transform(screen_df[['screen_width', 'screen_height']])
            
            print("normalized screen size")
            return screen_df[['screen_width', 'screen_height']]
        else:
            raise ValueError("Screen size does not contain 'screen_width' and 'screen_height' keys.")

    def get_normalized_data(self, data):
        if 'screen_width' not in data or 'screen_height' not in data:
            raise KeyError("The dataset does not contain 'screen_width' or 'screen_height'. Check JSON structure.")

        screen_size = {"screen_width": data['screen_width'], "screen_height": data['screen_height']}
        elements = data['elements']

        # Normalize the elements first
        normalized_elements = self.normalize_ui_elements(elements)
        
        # Normalize the screen size and add it to the DataFrame
        normalized_screen_size = self.normalize_screen_size(screen_size)
        
        print("normalized elements and screen size : ")
        return normalized_elements, normalized_screen_size




