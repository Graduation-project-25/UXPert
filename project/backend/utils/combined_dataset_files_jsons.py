import os
import shutil

# Define the source folder (Full) and target folder (jsons)
source_folder = ".data/raw/MASC/MASC_Json/MASC_Json/Full"
target_folder = "./data/raw/MASC/MASC_Json/jsons"

# Create the 'jsons' folder if it doesn't exist
os.makedirs(target_folder, exist_ok=True)

# Walk through the subfolders in 'Full'
for root, dirs, files in os.walk(source_folder):
    for file in files:
        # Process only JSON files
        if file.lower().endswith(".json"):
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_folder, file)

            # Avoid overwriting if file already exists
            if os.path.exists(target_file_path):
                print(f"JSON file {file} already exists in the target folder, skipping.")
            else:
                # Move the JSON file to the target folder
                shutil.move(source_file_path, target_file_path)
                print(f"Moved JSON file: {file}")

print(f"All JSON files from '{source_folder}' and its subfolders have been moved to '{target_folder}'.")
