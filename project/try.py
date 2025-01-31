import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
import sys
import os

# Ensure the correct module paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from components.Clustering_Component.EGFE_clustering import EGFEClustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFEClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFEClusteringTesting
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction  # ✅ Import the correct class

# Load config
config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

# Initialize Flask
app = Flask(__name__)
CORS(app, supports_credentials=True)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/") 
db = client[config["DATABASE_NAME"]]  
designs_collection = db[config["COLLECTION_NAME"]]  
# Create instances of classes
clustering = EGFEClustering()
evaluation = EGFEClusteringEvaluation()
testing = EGFEClusteringTesting()
feature_extractor = EGFE_FeatureExtraction()  # ✅ Create an instance of the Feature Extractor

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  

    try:
        # Parse JSON data from request
        data = request.get_json()
        user_name = data.get('user_name', "Unknown User")
        design_name = data.get('design_name', "Untitled Design")
        elements = data.get('elements', [])

        if not elements:
            return jsonify({"error": "No elements provided"}), 400

        print(f"Processing design from {user_name}: {design_name}")

        # Convert JSON data to DataFrame
        df = pd.DataFrame(elements)

        # Step 1: Normalize Data (Use class instance) ✅
        normalized_df = feature_extractor.normalize_ui_elements(elements, df)

        # Step 2: Aggregate Data (Use class instance) ✅
        aggregated_df = feature_extractor.aggregate_ui_elements(normalized_df)

        # Step 3: Apply DBSCAN Clustering
        X_train, DBSCAN_dataset, clusters = clustering.dbscan_cluster(aggregated_df)

        # Step 4: Evaluate Clustering
        evaluation.evaluate_clustering(DBSCAN_dataset)

        # Step 5: Analyze Clusters (Consistency Scores)
        clustering.analyze_clusters(DBSCAN_dataset)

        # Save Extracted Features & Clustering Results to MongoDB
        features_entry = {
            "user_name": user_name,
            "design_name": design_name,
            "timestamp": datetime.utcnow(),
            "normalized_data": normalized_df.to_dict(orient='records'),
            "aggregated_data": aggregated_df.to_dict(orient='records'),
            "clusters": clusters.tolist(),
        }

        designs_collection.insert_one(features_entry)

        return jsonify({
            "message": "Processing completed and stored in DB!",
            "status": 200,
            "clusters": clusters.tolist()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cluster', methods=['POST'])
def cluster_elements():
    try:
        # Receive Extracted Features
        data = request.get_json()
        df = pd.DataFrame(data)  # Convert JSON to DataFrame

        # Apply DBSCAN Clustering
        X_train, DBSCAN_dataset, clusters = clustering.dbscan_cluster(df)

        # Evaluate Clustering
        evaluation.evaluate_clustering(DBSCAN_dataset)

        # Analyze Clusters (Consistency Scores)
        clustering.analyze_clusters(DBSCAN_dataset)

        return jsonify({"message": "Clustering completed", "clusters": clusters.tolist()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/assign-test-clusters', methods=['POST'])
def assign_test_clusters():
    try:
        # Receive Training & Test Data
        data = request.get_json()
        X_train = pd.DataFrame(data['train'])
        X_test = pd.DataFrame(data['test'])

        # Assign Clusters to Test Elements
        assigned_clusters = testing.assign_test_clusters(X_train, X_test, None)

        return jsonify({
            "message": "Test Clustering Done",
            "clusters": assigned_clusters.to_dict(orient='records')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200


if __name__ == '__main__':
    app.run(debug=True, port=3000)
