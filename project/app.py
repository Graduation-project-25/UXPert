import os
import requests
from flask import Flask, request, jsonify
from components.Clustering_Component.EGFE_clustering import dbscan_cluster
from components.Feature_Extractor_Component.EGFE_ui_extraction import extract_egfe_ui_elements, aggregate_ui_elements
from components.Visualizer_Component.EGFE_visualization import scatter_plot_ui_elements

app = Flask(__name__)

# Figma API configuration
FIGMA_API_BASE = "https://api.figma.com/v1"
FIGMA_TOKEN = "figd_Bz3iqc9-MD4gr1P3CVPHoBjVq-bzkznu1dPWcX4d"  # Replace with your Figma Token

@app.route("/")
def home():
    return "Figma Integration Service is Running!"

# Fetch file details from Figma
@app.route("/figma/file/<file_key>", methods=["GET"])
def get_figma_file(file_key):
    url = f"{FIGMA_API_BASE}/files/{file_key}"
    headers = {"Authorization": f"Bearer {FIGMA_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch Figma file"}), response.status_code

# Extract UI elements and process them
@app.route("/figma/file/<file_key>/process", methods=["POST"])
def process_figma_file(file_key):
    url = f"{FIGMA_API_BASE}/files/{file_key}"
    headers = {"Authorization": f"Bearer {FIGMA_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch Figma file"}), response.status_code

    # Extract UI elements from Figma response
    figma_data = response.json()
    json_file_path = f"./data/figma_{file_key}.json"
    with open(json_file_path, "w") as f:
        f.write(response.text)

    elements, normalized_data = extract_egfe_ui_elements([json_file_path])
    aggregated_elements = aggregate_ui_elements(normalized_data)

    # Visualize data
    scatter_plot_ui_elements(normalized_data)

    # Perform clustering
    clustered_data, dbscan_dataset, clusters = dbscan_cluster(normalized_data)

    return jsonify({
        "status": "success",
        "aggregated_elements": aggregated_elements.to_dict(),
        "clusters": clusters,
    })

# Open a Figma file directly in Figma Desktop
@app.route("/figma/open/<file_key>", methods=["GET"])
def open_figma_file(file_key):
    figma_url = f"figma://file/{file_key}"
    return jsonify({"figma_url": figma_url})

if __name__ == "__main__":
    app.run(debug=True)

# curl -H "Authorization: Bearer <figd_Bz3iqc9-MD4gr1P3CVPHoBjVq-bzkznu1dPWcX4d>" "https://api.figma.com/v1/files/<YOUR_FILE_KEY>"
