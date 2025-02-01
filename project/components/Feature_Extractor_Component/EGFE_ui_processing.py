import json
import os
from PIL import Image

from components.Feature_Extractor_Component.ui_processor import UiProcessorInterface
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction

class EGFE_UiProcessing(UiProcessorInterface):
    egfe_ui_extraction = EGFE_FeatureExtraction()
    
    def save_ui_elements(self, elements,image_name, output_path):
        # print(image_name)
        # """Saves the extracted UI elements along with screen size to a JSON file."""
        width,height = self.estimate_screen_size(image_name)
        data_to_save = {
            "screen_size": {"width": width, "height": height},
            "elements": elements
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

        # print(f"Saved extracted elements and screen size to: {output_path}")


    def estimate_screen_size(self, image_name):
        image_path = f"data/raw/EGFE/images/{image_name}.png"
        # Load an image
        image = Image.open(image_path)

        # Get the size of the image
        width, height = image.size

        # print(f"The image resolution is: {width}x{height}")
        return width, height


    def process_ui_elements(self, json_folder, output_folder):
        # """Processes UI JSON files, extracts elements, estimates screen size, and saves the results."""
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

        for json_file in json_files:
            json_file_path = os.path.join(json_folder, json_file)
            output_path = os.path.join(output_folder, json_file)

            try:
                # print(f"Processing: {json_file_path}")
                image_name = os.path.splitext(json_file)[0]
                # Extract UI elements
                ui_elements, normalized_data = self.egfe_ui_extraction.extract_ui_elements(json_file_path)                
                # Save the extracted elements and screen size
                self.save_ui_elements(ui_elements,image_name, output_path)

            except Exception as e:
                print(f"Error processing {json_file_path}")

    