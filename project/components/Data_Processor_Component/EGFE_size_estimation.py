import os
from PIL import Image
import numpy as np

from components.Data_Processor_Component.screen_size_estimator import SizeEstimatorInterface


class EGFE_SizeEstimation(SizeEstimatorInterface):
    def __init__(self):
        self.dataset_folder = './data/raw/EGFE'
        self.image_folder  = self.dataset_folder + '/images'  
        self.mean_width, self.mean_height = self._calculate_mean_size()
    
    def get_image_size(self, image_name):
        image_path = os.path.join(self.image_folder, f"{image_name}.png")
        try:
            # Load an image
            image = Image.open(image_path)
            # Get the size of the image
            width, height = image.size
        except FileNotFoundError:
            width, height = self.mean_width, self.mean_height
        return width, height
    
    
    # Estimate the missing image with mean width and height of all images in the dataset
    def _calculate_mean_size(self):
        widths, heights = [], []
        for file in os.listdir(self.image_folder):
            if file.endswith(".png"):
                try:
                    with Image.open(os.path.join(self.image_folder, file)) as img:
                        width, height = img.size
                        widths.append(width)
                        heights.append(height)
                except Exception as e:
                    print(f"Error processing {file}: {e}")

        if widths and heights:
            return int(np.mean(widths)), int(np.mean(heights))
        else:
            print(f"Warning: Image not found. Returning Default size.")
            return 1920, 1080  # Default fallback resolution


    def estimate_screen_size(self, image_name, elements):
        estimated_screen_width, estimated_screen_height = self.get_image_size(image_name)
        for element in elements:
            element_width = element['width']
            element_height = element['height']
            element_name = element['name'].lower()
            if("frame" in element_name or "background" in element_name or "bg" in element_name):
                estimated_screen_width = element_width
                estimated_screen_height = element_height

            if(estimated_screen_width < element_width  and estimated_screen_height < element_height):
                estimated_screen_width = element_width
                estimated_screen_height = element_height
        return estimated_screen_width, estimated_screen_height



