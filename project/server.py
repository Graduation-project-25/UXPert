import json
import requests
from pymongo import MongoClient

# Load configuration from the .config file
config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Set up headers for Figma API request
headers = {
    'X-Figma-Token': config["FIGMA_TOKEN"]
}

# Make a request to the Figma API
response = requests.get(f'https://api.figma.com/v1/files/{config["FILE_KEY"]}', headers=headers)

if response.status_code == 200:
    
    data = response.json()
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

    # Connect to MongoDB
    client = MongoClient(config["MONGODB_URI"])  # Connect to MongoDB using the provided URI
    db = client[config["DATABASE_NAME"]]  # Access the specified database
    collection = db[config["COLLECTION_NAME"]]  # Access the specified collection
    
    # Insert the features into the MongoDB collection
    collection.insert_one(features)  # Insert the features dictionary as a document
    print("Features have been saved to MongoDB.")
    
else:
    print('Error:', response.status_code, response.text)
