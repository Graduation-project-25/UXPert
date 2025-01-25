import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler



def extract_json_file_path(json_folder,limit=50):
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')][:limit]
    index =0
    if index >= len(json_files):
        index = 0
    json_file_path = os.path.join(json_folder, json_files[index])
    return json_file_path

# def extract_ui_elements(json_file_path, dataset_type):
#     """Extracts UI elements from a given JSON file."""
#     elements = []

#     if dataset_type == 'EGFE':
#         elements = extract_egfe_ui_elements(json_file_path)
#     elif dataset_type == 'Rico':
#         elements = extract_rico_ui_elements(json_file_path)

#     print (elements)
#     print("Extracted Elements:\n", json.dumps(elements, indent=4))

#     # Normalize json data into a flat table
#     df = pd.json_normalize(elements)

#     # Normalize into scaled data 
#     normalized_data = normalize_ui_elements(elements, df)
#     print("Normalized, Scaled Data:\n", normalized_data)
#     print("***************************************************************\n")    
    
#     return elements, normalized_data

def extract_egfe_ui_elements(json_file_path):
    """Extracts UI elements from a given JSON file."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
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
    #print (elements)
    #print("Extracted Elements:\n", json.dumps(elements, indent=4))

    # Normalize json data into a flat table
    df = pd.json_normalize(elements)

    # Normalize into scaled data 
    normalized_data = normalize_ui_elements(elements, df)
    print("Normalized, Scaled Data:\n", normalized_data)
    print("***************************************************************\n")    


    
    return elements, normalized_data


def normalize_ui_elements(elements, df):
    # Scaling width, height, position.x, position.y
    scale = MinMaxScaler()
    X = df[['width', 'height', 'position.x', 'position.y']]
    df[['width', 'height', 'position.x', 'position.y']] = scale.fit_transform(X)
    df[['color_r', 'color_g', 'color_b', 'color_a']] = pd.DataFrame(df['color'].tolist(), index=df.index) # RGBA
    df = pd.get_dummies(df, columns=['type'], prefix='type') #One-hot encode the 'type' column
    df = df.astype({col: 'int' for col in df.columns if col.startswith('type_')}) # Convert Boolean columns to 0 and 1
    return df

def save_ui_elements(elements, output_path):
    """Saves the extracted UI elements to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(elements, f, ensure_ascii=False, indent=4)
    print(f"Saved extracted elements to: {output_path}")


def aggregate_ui_elements(df):
    """Aggregate UI elements by name and compute average position and size."""
    aggregated = df.groupby('name').agg({
        'position.x': 'mean',
        'position.y': 'mean',
        'width': 'mean',
        'height': 'mean'
    }).reset_index()
    return aggregated

def split_dataset(df):
    X=df
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
    return X_train, X_test