import json
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

        # Extract screen size
        screen_size = data.get("screen_size", {"screen_width": 0, "screen_height": 0})

        # Extract elements
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
        # print (elements)
        # print("Extracted Elements:\n", json.dumps(elements, indent=4))
        return elements

    def extract_elements_and_screen_size (self, json_file_path):
        """Extracts UI elements and Screen Size from a given JSON file."""

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract screen size
        screen_size = data.get("screen_size", {"width": 0, "height": 0})

        # Extract elements
        elements = []
        for element in data.get("elements", []):
            extracted_element = {
                "type": element.get("type", ""),
                "position": {
                    "x": element.get("position", {}).get("x", 0),
                    "y": element.get("position", {}).get("y", 0)
                },
                "width": element.get("width", 0),
                "height": element.get("height", 0),
                "name": element.get("name", ""),
                "color": element.get("color", [0, 0, 0, 1])  # Default to black (RGBA)
            }
            elements.append(extracted_element)

        # print("Extracted Elements:\n", json.dumps(elements, indent=4))  
        # print("\nScreen Size:\n", json.dumps(screen_size, indent=4))  

        return screen_size, elements
# import os
# import json
# import pandas as pd
# from components.Feature_Extractor_Component.feature_extractor import FeatureExtractorInterface


# class EGFE_FeatureExtraction(FeatureExtractorInterface):
#     # def __init__(self):
#     #     pass

#     def extract_elements_and_screen_size(self, json_file_path):
#         """Extracts UI elements and screen size from a given JSON file."""
#         with open(json_file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)

#         # Extract screen size
#         screen_size = data.get("screen_size", {"width": 0, "height": 0})

#         # Extract elements
#         elements = []
#         for element in data.get("elements", []):
#             extracted_element = {
#                 "type": element.get("type", ""),
#                 "position": {
#                     "x": element.get("position", {}).get("x", 0),
#                     "y": element.get("position", {}).get("y", 0)
#                 },
#                 "width": element.get("width", 0),
#                 "height": element.get("height", 0),
#                 "name": element.get("name", ""),
#                 "color": element.get("color", [0, 0, 0, 1])
#             }
#             elements.append(extracted_element)

#         return {
#             "screen_width": screen_size.get("width", 0),
#             "screen_height": screen_size.get("height", 0),
#             "elements": elements
#         }

#     def load_json_from_folder(self, folder_path):
#         """Load all JSON files from the specified folder."""
#         json_data = []
        
#         for file_name in os.listdir(folder_path):
#             if file_name.endswith('.json'):
#                 file_path = os.path.join(folder_path, file_name)
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     json_data.append(json.load(f))
        
#         return json_data
#     # def extract_json_file_paths(self, json_folder):
#     #     # List all JSON files in the directory
#     #     json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
        
#     #     if not json_files:  # Check if there are no JSON files
#     #         raise FileNotFoundError("No JSON files found in the folder.")
        
#     #     # Return full paths to each JSON file
#     #     json_file_paths = [os.path.join(json_folder, f) for f in json_files]
#     #     return json_file_paths


#     # #extracts ui from json
#     # def extract_ui_elements(self, json_file_path):
#     #     """Extracts UI elements from a given JSON file."""
#     #     with open(json_file_path, 'r', encoding='utf-8') as f:
#     #         data = json.load(f)

#     #     # Extract screen size
#     #     screen_size = data.get("screen_size", {"screen_width": 0, "screen_height": 0})

#     #     # Extract elements
#     #     elements = []
#     #     for layer in data.get('layers', []):
#     #         rect = layer.get('rect', {})
#     #         element = {
#     #             'type': layer.get('_class', ''),
#     #             'position': {
#     #                 'x': rect.get('x', 0),
#     #                 'y': rect.get('y', 0)
#     #             },
#     #             'width': rect.get('width', 0),
#     #             'height': rect.get('height', 0),
#     #             'name': layer.get('name', ''),  # Using 'name' as the text/label
#     #             'color': layer.get('color', '')
#     #         }
#     #         elements.append(element)
#     #     # print (elements)
#     #     # print("Extracted Elements:\n", json.dumps(elements, indent=4))
#     #     return elements
