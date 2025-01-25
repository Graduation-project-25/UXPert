import os
import shutil

# Define the base folder and target folders for images and JSON files
base_folder = "./data/raw/MASC"
images_folder = os.path.join(base_folder, "images")
jsons_folder = os.path.join(base_folder, "jsons")

# Create the 'images' and 'jsons' folders if they don't exist
os.makedirs(images_folder, exist_ok=True)
os.makedirs(jsons_folder, exist_ok=True)

# Iterate through subfolders and move images and JSON files
for root, dirs, files in os.walk(base_folder):
    # Keep track of images and their corresponding JSON files
    image_files = {file for file in files if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))}
    json_files = {file for file in files if file.lower().endswith(".json")}
    
    for image_file in image_files:
        # Ensure the corresponding JSON file exists for the image
        base_name = os.path.splitext(image_file)[0]
        json_file = f"{base_name}.json"
        
        image_path = os.path.join(root, image_file)
        json_path = os.path.join(root, json_file)
        
        # Move image if not already in the images folder
        if os.path.exists(image_path) and not os.path.exists(os.path.join(images_folder, image_file)):
            shutil.move(image_path, images_folder)
            print(f"Moved image file {image_file}.")
        
        # Move JSON if corresponding JSON exists and not already in the jsons folder
        if os.path.exists(json_path) and not os.path.exists(os.path.join(jsons_folder, json_file)):
            shutil.move(json_path, jsons_folder)
            print(f"Moved JSON file {json_file}.")

print(f"All matching image and JSON files have been moved to {images_folder} and {jsons_folder}.")
