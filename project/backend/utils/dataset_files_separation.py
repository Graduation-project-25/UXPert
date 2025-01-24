import os
import shutil
import cv2
import json
import numpy as np
import pytesseract

# Adjust the paths if needed
dataset_folder = './project/data/raw/EGFE'  # Adjust the path if needed
image_folder  = dataset_folder + '/images'  # Folder for images
json_folder  = dataset_folder + '/jsons'  # Folder for JSON files
output_folder = dataset_folder + '/extractedFeatures'

# Create output directories if they don't exist
os.makedirs(image_folder, exist_ok=True)
os.makedirs(json_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Iterate through files in the dataset folder
for filename in os.listdir(dataset_folder):
    file_path = os.path.join(dataset_folder, filename)

    # Check if it's a file and separate based on the file extension
    if os.path.isfile(file_path):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            shutil.move(file_path, image_folder)
        elif filename.endswith('.json'):
            shutil.move(file_path, json_folder)

print("Files have been separated into 'images' and 'jsons' folders.")