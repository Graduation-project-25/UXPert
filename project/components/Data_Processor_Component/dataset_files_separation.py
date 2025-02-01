import os
import shutil
import numpy as np
from data_processor import DataProcessor

class FileSeparator(DataProcessor):
    def __init__(self, dataset_folder):
        self.dataset_folder = dataset_folder
        self.image_folder = os.path.join(dataset_folder, 'images')  # Folder for images
        self.json_folder = os.path.join(dataset_folder, 'jsons')    # Folder for JSON files
        self.output_folder = os.path.join(dataset_folder, 'extractedFeatures')

        # Create output directories if they don't exist
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(self.json_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def process(self):
        # Iterate through files in the dataset folder
        for filename in os.listdir(dataset_folder):
            file_path = os.path.join(dataset_folder, filename)

            # Check if it's a file and separate based on the file extension
            if os.path.isfile(file_path):
                if filename.endswith('.png') or filename.endswith('.jpg'):
                    shutil.move(file_path, self.image_folder)
                    shutil.move(file_path, self.image_folder)
                elif filename.endswith('.json'):
                    shutil.move(file_path, self.json_folder)

        print("Files have been separated into 'images' and 'jsons' folders.")

if __name__ == "__main__":
    # Adjust the paths if needed
    dataset_folder = './data/raw/EGFE' 
    # dataset_folder = './data/raw/RICO/unique_uis/combined' 
    # dataset_folder = './data/raw/MASC' 

    # Create an instance of FileSeparator and call its process method
    file_separator = FileSeparator(dataset_folder)
    file_separator.process()
