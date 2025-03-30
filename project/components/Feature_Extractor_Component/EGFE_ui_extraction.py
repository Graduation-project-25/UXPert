import json
import math
import os

from components.Feature_Extractor_Component.feature_extractor import FeatureExtractorInterface


class EGFE_FeatureExtraction(FeatureExtractorInterface):
    def extract_json_file_paths(self, json_folder):
        # List all JSON files in the directory
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
        
        if not json_files:  # Check if there are no JSON files
            raise FileNotFoundError("No JSON files found in the folder.")
        
        # Return full paths to each JSON file
        json_file_paths = [os.path.join(json_folder, f) for f in json_files]
        return json_file_paths

    #extracts ui from json
    def extract_ui_elements(self, json_file_path):
        """Extracts UI elements from a given JSON file."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract elements
        elements = []
        icons, text_elements = self.get_icons_and_texts(data)
        for layer in data.get('layers', []):
            rect = layer.get('rect', {})
            type = layer.get('_class', '')
            element = {
                'type': type,
                'position': {
                    'x': rect.get('x', 0),
                    'y': rect.get('y', 0)
                },
                'width': rect.get('width', 0),
                'height': rect.get('height', 0),
                'name': layer.get('name', ''),  # Using 'name' as the text/label
                'color': layer.get('color', ''),
                'labeled': self.is_icon_labeled(layer, text_elements) if type == 'symbolInstance' else False
            }
            elements.append(element)
        # print (elements)
        # print("Extracted Elements:\n", json.dumps(elements, indent=4))
        return elements
    

    def get_icons_and_texts(self, data):
        icons = []
        text_elements = []

        for layer in data.get('layers', []):
            if layer.get('_class', '') == 'symbolInstance':
                icons.append(layer)
            elif layer.get('_class', '') == 'text':
                text_elements.append(layer)

        return icons, text_elements

    def is_icon_labeled(self, icon, text_elements, threshold=50):
        """Checks if a given icon has a nearby text label."""
        icon_x, icon_y = icon['rect']['x'], icon['rect']['y']

        for text in text_elements:
            text_x, text_y = text['rect']['x'], text['rect']['y']
            distance = math.sqrt((icon_x - text_x) ** 2 + (icon_y - text_y) ** 2)

            if distance < threshold:
                return True  # Labeled

        return False  # Not labeled
        
    def is_shape_and_text_overlapping(shape, text):
        """Check if the text is inside the shape's bounding box."""
        shape_x, shape_y, shape_w, shape_h = shape["rect"]["x"], shape["rect"]["y"], shape["rect"]["width"], shape["rect"]["height"]
        text_x, text_y, text_w, text_h = text["rect"]["x"], text["rect"]["y"], text["rect"]["width"], text["rect"]["height"]

        return (text_x >= shape_x and text_x + text_w <= shape_x + shape_w and
                text_y >= shape_y and text_y + text_h <= shape_y + shape_h)
    

    def classify_shapes_as_buttons(layers):
        buttons = []
        
        shapes = [layer for layer in layers if layer["_class"] in ["oval", "rectangle"]]
        texts = [layer for layer in layers if layer["_class"] == "text"]
        
        for shape in shapes:
            for text in texts:
                if is_overlapping(shape, text):
                    shape["_class"] = "button"  # Convert shape to button
                    buttons.append({
                        "id": shape["id"],
                        "name": shape["name"],
                        "text": text["text"]
                    })
        
        return buttons

