import json
import os
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

from .EGFE_Clustering import save_cluster_as_json



pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200) 


dataset_folder = './project/data/raw/EGFE'  # Adjust the path if needed
image_folder  = dataset_folder + '/images'  # Folder for images
json_folder  = dataset_folder + '/jsons'  # Folder for JSON files
output_folder = dataset_folder + '/extractedFeatures'
os.makedirs(output_folder, exist_ok=True)

def assign_test_clusters(X_train, X_test, dbscan):
    # Compute the cluster centers from `X_train`
    unique_clusters = X_train['Cluster'].unique()
    cluster_centers = {
        cluster: X_train[X_train['Cluster'] == cluster].mean(axis=0) 
        for cluster in unique_clusters 
        # if cluster != -1  # Exclude noise
    }
    # Calculate distances from `X_test` samples to cluster centers
    test_features = X_test[['width', 'height', 'position.x', 'position.y']+ 
                 [col for col in X_train.columns if col.startswith('color_')] + 
                 [col for col in X_train.columns if col.startswith('type_')] ].values
    cluster_centers_array = np.array(list(cluster_centers.values()))[:,:-1]
    distances = cdist(test_features, cluster_centers_array)

    # Assign clusters based on the minimum distance
    assigned_clusters = distances.argmin(axis=1)
    X_test['Assigned_Cluster'] = assigned_clusters

    return X_test

def evaluate_test_clusters(X_test, X_train):
    # Compare cluster consistency or use metrics like silhouette scores
    train_clusters = X_train['Cluster'].unique()
    test_clusters = X_test['Assigned_Cluster'].unique()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cluster_json_path = os.path.join(script_dir, "X-test clusters.json")      
    save_cluster_as_json(X_test,cluster_json_path,'Assigned_Cluster')


    print("Clusters in training data:", train_clusters)
    print("Clusters assigned to test data:", test_clusters)
