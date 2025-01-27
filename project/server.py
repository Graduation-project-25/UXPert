import json
import requests

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

headers = {
    'X-Figma-Token': config["FIGMA_TOKEN"]
}

response = requests.get(f'https://api.figma.com/v1/files/{config["FILE_KEY"]}', headers=headers)

if response.status_code == 200:
    
    data = response.json()
    print(data)
    # Format the extracted features (you can modify this depending on which data you want to extract)
    features = {
        'document': data.get('document', {}),
        'last_modified': data.get('lastModified', ''),
        'name': data.get('name', ''),
        'file_key': config["FILE_KEY"]
    }
    
    # Save the features to a JSON file
    with open('figma_features.json', 'w') as json_file:
        json.dump(features, json_file, indent=4)
    
    print("Features have been saved to 'figma_features.json'.")
else:
    print('Error:', response.status_code, response.text)
