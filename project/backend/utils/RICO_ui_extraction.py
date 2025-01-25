import json

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def extract_rico_ui_elements(json_file_path):
    """Extract UI elements from Rico dataset."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = []

    def traverse(node):
        if isinstance(node, dict):
            bounds = node.get("bounds", [0, 0, 0, 0])
            element = {
                "type": node.get("class", ""),
                "position": {"x": bounds[0], "y": bounds[1]},
                "width": bounds[2] - bounds[0],
                "height": bounds[3] - bounds[1],
                "name": node.get("text", node.get("content-desc", "")),
                "clickable": node.get("clickable", False),
                "visibility": node.get("visibility", ""),
                "enabled": node.get("enabled", True),
            }
            elements.append(element)

            # Recursively process children
            for child in node.get("children", []):
                traverse(child)

    # Start traversal from the root element
    if "activity" in data and "root" in data["activity"]:
        traverse(data["activity"]["root"])


    # Normalize json data into a flat table
    df = pd.json_normalize(elements)

    # Normalize into scaled data 
    normalized_data = normalize_ui_elements(elements, df)
    # print("Normalized, Scaled Data:\n", normalized_data)
    # print("***************************************************************\n")    
    
    return elements, normalized_data

def normalize_ui_elements(elements, df):
    """Normalize the UI elements' positional and dimensional data."""
    # Instantiate a scaler for the numerical columns: width, height, x, and y
    scaler = MinMaxScaler()

    # Select only the numeric columns for scaling
    numeric_cols = ['width', 'height', 'position.x', 'position.y']
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    # df = pd.get_dummies(df, columns=['type'], prefix='type')
    df['clickable'] = df['clickable'].astype(int)
    df['enabled'] = df['enabled'].astype(int)


    # Return the normalized and scaled data as a DataFrame
    return df
