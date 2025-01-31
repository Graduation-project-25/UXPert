import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from components.Clustering_Component.EGFE_clustering import EGFEClustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFEClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFEClusteringTesting

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Initialize the Flask application
app = Flask(__name__)

CORS(app, supports_credentials=True)
clustering = EGFEClustering()
evaluation = EGFEClusteringEvaluation()
testing = EGFEClusteringTesting()

@app.route('/cluster', methods=['POST'])
def cluster_elements():
    try:
        # Step 1: Receive Extracted Features
        data = request.get_json()
        df = pd.DataFrame(data)  # Convert JSON to DataFrame

        # Step 2: Apply DBSCAN Clustering
        X_train, DBSCAN_dataset, clusters = clustering.dbscan_cluster(df)

        # Step 3: Evaluate Clustering Quality
        evaluation.evaluate_clustering(DBSCAN_dataset)

        # Step 4: Analyze Clusters (Consistency Scores)
        clustering.analyze_clusters(DBSCAN_dataset)

        return jsonify({"message": "Clustering completed", "clusters": clusters.tolist()})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/assign-test-clusters', methods=['POST'])
def assign_test_clusters():
    try:
        # Step 1: Receive Training & Test Data
        data = request.get_json()
        X_train = pd.DataFrame(data['train'])
        X_test = pd.DataFrame(data['test'])

        # Step 2: Assign Clusters to Test Elements
        assigned_clusters = testing.assign_test_clusters(X_train, X_test, None)

        return jsonify({"message": "Test Clustering Done", "clusters": assigned_clusters.to_dict(orient='records')})

    except Exception as e:
        return jsonify({"error": str(e)})
    

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  

    # Parse JSON data from the request
    data = request.get_json()
    user_name = data.get('user_name', "Unknown User")
    design_name = data.get('design_name', "Untitled Design")
    elements = data.get('elements', [])

    if not elements:
        return jsonify({"error": "Missing user_name or elements"}), 400

    # Log the received elements
    print(f"Received design from {user_name} : {design_name}")
    for index, element in enumerate(elements):
        print(f"Element {index + 1}: {element}")

    # Save the features to a JSON file
    features = {
        "user_name": user_name,
        "design_name": design_name,
        "elements": elements,
        
    }

    with open('design_features.json', 'w') as json_file:
        json.dump(features, json_file, indent=4)
    
    print("Design features have been saved to 'design_features.json'.")

    return jsonify({
        "message": "Design features saved successfully!",
        "status": 200
    }), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
