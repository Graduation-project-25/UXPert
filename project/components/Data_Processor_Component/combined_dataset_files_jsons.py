import os
import shutil

# Define the base folder and target folder for JSON files
base_folder = "./data/raw/MASC"
jsons_folder = os.path.join(base_folder, "jsons")

# Create the 'jsons' folder if it doesn't exist
os.makedirs(jsons_folder, exist_ok=True)

# Iterate through all files in subfolders of the base folder
for root, dirs, files in os.walk(base_folder):
    for file in files:
        # Check if the file is a JSON file
        if file.lower().endswith(".json"):
            source_path = os.path.join(root, file)
            destination_path = os.path.join(jsons_folder, file)
            
            # Move JSON file to the 'jsons' folder, avoid overwriting
            if os.path.exists(destination_path):
                print(f"JSON file {file} already exists in the target folder, skipping.")
            else:
                shutil.move(source_path, destination_path)
                print(f"Moved JSON file: {file}")

print(f"All JSON files from '{base_folder}' and its subfolders have been moved to '{jsons_folder}'.")
