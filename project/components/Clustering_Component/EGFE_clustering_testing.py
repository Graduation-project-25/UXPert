import os
import json
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from components.Clustering_Component.clustering_testing import ClusteringTestingInterface
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from sklearn.metrics import silhouette_score, davies_bouldin_score


class EGFE_ClusteringTesting(ClusteringTestingInterface):
    def __init__(self):
        self.egfe_load_data = EGFE_LoadData()
        # self.egfe_clustering = EGFE_Clustering(self.train_folder,self.output_folder)

    # def assign_test_clusters(self, train_folder, X_test, dbscan):
    #     print("s")
    #     X_train = self.data_loader.load_data(train_folder)
    #     # Compute the cluster centers from `X_train`
    #     unique_clusters = X_train['Cluster'].unique()
    #     cluster_centers = {
    #         cluster: X_train[X_train['Cluster'] == cluster].mean(axis=0) 
    #         for cluster in unique_clusters 
    #         # if cluster != -1  # Exclude noise
    #     }
    #     # Calculate distances from `X_test` samples to cluster centers
    #     test_features = X_test[['width', 'height', 'position.x', 'position.y']+ 
    #                 [col for col in X_train.columns if col.startswith('color_')] + 
    #                 [col for col in X_train.columns if col.startswith('type_')] ].values
    #     cluster_centers_array = np.array(list(cluster_centers.values()))[:,:-1]
    #     distances = cdist(test_features, cluster_centers_array)

    #     # Assign clusters based on the minimum distance
    #     assigned_clusters = distances.argmin(axis=1)
    #     X_test['Assigned_Cluster'] = assigned_clusters

    #     return X_test


    def assign_test_clusters(self, train_data, test_folder, feature):
        #  Load test data from the folder
        X_test = self.egfe_load_data.load_data(test_folder)
        # print("X test:")
        # print(X_test)
        # Keep train data unchanged
        X_train = train_data

        #  Select features based on feature type
        if feature == "color":
            selected_features = [col for col in X_train.columns if col.startswith('color_')] + \
                                [col for col in X_train.columns if col.startswith('type_')]
        elif feature == "size":
            selected_features = [col for col in X_train.columns if col.startswith('width')] + \
                                [col for col in X_train.columns if col.startswith('hight')]+\
                                [col for col in X_train.columns if col.startswith('type_')]
        elif feature == "position":
            selected_features = [col for col in X_train.columns if col.startswith('position.x')] + \
                                [col for col in X_train.columns if col.startswith('position.y')]+\
                                [col for col in X_train.columns if col.startswith('type_')]
        else:
            raise ValueError("Invalid feature type. Choose from 'color', 'size', or 'position'.")
        
        #  Ensure the selected features exist in X_test
        # Add missing features as columns with all 0 values
        missing_features = [col for col in selected_features if col not in X_test.columns]
        for feature in missing_features:
            X_test[feature] = 0
        # Extract relevant features for clustering
        X_train_selected = X_train[selected_features]
        X_test_selected = X_test[selected_features]

        # Convert all feature columns to numeric and replace NaN with 0 for all columns
        X_test_selected = X_test_selected.apply(pd.to_numeric, errors='coerce').fillna(0)
        X_train_selected = X_train_selected.apply(pd.to_numeric, errors='coerce').fillna(0)
        

        # Make sure all the features have no NaN (in case they are missing from test data but present in train data)
        for column in selected_features:
            if column not in X_test_selected:
                X_test_selected[column] = 0  # Ensure missing columns are filled with 0
            else:
                X_test_selected[column] = X_test_selected[column].fillna(0)  # Fill NaN with 0 in existing columns
        
        for column in selected_features:
            if column not in X_train_selected:
                X_train_selected[column] = 0  # Ensure missing columns in X_train are also filled with 0
            else:
                X_train_selected[column] = X_train_selected[column].fillna(0)
        #  Compute cluster centers from training data
        unique_clusters = X_train['Cluster'].unique()
        cluster_centers = {
            cluster: X_train_selected[X_train['Cluster'] == cluster].mean(axis=0) 
            for cluster in unique_clusters
        }

        #  Convert data to numpy arrays for distance computation
        cluster_centers_array = np.array(list(cluster_centers.values()), dtype=np.float64)
        test_features = X_test_selected.values.astype(np.float64)

        #  Compute distances and assign clusters
        distances = cdist(test_features, cluster_centers_array)
        assigned_clusters = distances.argmin(axis=1)

        #  Assign clusters to X_test
        X_test['Assigned_Cluster'] = assigned_clusters
        # print("X test after clustering")
        # print(X_test)
        return X_test
    
    def save_clusters_to_json(self, X_test, output_folder, feature):
        # Create a dictionary to hold the clusters
        clusters_dict = {}

        # Group the data by the assigned cluster and store the features in the cluster dictionary
        for _, row in X_test.iterrows():
            cluster_id = row['Assigned_Cluster']
            # Get the row data (excluding 'Assigned_Cluster' column) and convert to a dictionary
            row_data = row.drop('Assigned_Cluster').to_dict()

            # Only keep the columns that are part of the selected feature for clustering
            if feature == "color":
                # Keep only the color-related columns
                row_data = {key: value for key, value in row_data.items() if key.startswith('color_') or key.startswith('type_')}
            elif feature == "size":
                # Keep only the size-related columns (e.g., 'width', 'height')
                row_data = {key: value for key, value in row_data.items() if key in ['width', 'height'] or key.startswith('type_')}
            elif feature == "position":
                # Keep only the position-related columns (e.g., 'position.x', 'position.y')
                row_data = {key: value for key, value in row_data.items() if key in ['position.x', 'position.y'] or key.startswith('type_')}

            # Replace any NaN values with 0 in the row_data
            row_data = {key: 0 if value != value else value for key, value in row_data.items()}

            # Add the row data to the corresponding cluster list
            if cluster_id not in clusters_dict:
                clusters_dict[cluster_id] = []
            clusters_dict[cluster_id].append(row_data)

        # Define the output file path
        output_file = os.path.join(output_folder, "size_test_clusters.json")
        
        # Save the clusters dictionary to the output folder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clusters_dict, f, ensure_ascii=False, indent=4)

        print(f"Clusters saved to {output_file}")


    # def save_cluster_as_json(self, clusters, cluster_json_path, group_by):
    #         clusters_dict = clusters.groupby(group_by).apply(lambda df: df.to_dict(orient='records'), include_groups=False).to_dict()
    #         with open(cluster_json_path, 'w', encoding='utf-8') as json_file:
    #             json.dump(clusters_dict, json_file, indent=4, ensure_ascii=False)


    # def assign_test_color_clusters(self, X_train, X_test_folder):
    #     X_test = self.data_loader.load_data(X_test_folder)
    #     # Compute the cluster centers from `X_train`
    #     unique_clusters = X_train['Cluster'].unique()
    #     cluster_centers = {
    #         cluster: X_train[X_train['Cluster'] == cluster].mean(axis=0) 
    #         for cluster in unique_clusters 
    #         # if cluster != -1  # Exclude noise
    #     }
    #     # Calculate distances from `X_test` samples to cluster centers
    #     test_features = X_test[['width', 'height', 'position.x', 'position.y']+ 
    #                 [col for col in X_train.columns if col.startswith('color_')] + 
    #                 [col for col in X_train.columns if col.startswith('type_')] ].values
    #     cluster_centers_array = np.array(list(cluster_centers.values()))[:,:-1]
    #     distances = cdist(test_features, cluster_centers_array)

    #     # Assign clusters based on the minimum distance
    #     assigned_clusters = distances.argmin(axis=1)
    #     X_test['Assigned_Cluster'] = assigned_clusters

    #     return X_test

    


    # def evaluate_test_clusters(self, X_test, X_train):
    #     # Ensure the necessary columns exist
    #     if 'Cluster' not in X_train.columns:
    #         raise ValueError("X_train does not contain the 'Cluster' column. Check the data source.")
    #     if 'Assigned_Cluster' not in X_test.columns:
    #         raise ValueError("X_test does not contain the 'Assigned_Cluster' column. Check the data source.")

    #     # Extract cluster labels
    #     train_clusters = X_train['Cluster'].unique()
    #     test_clusters = X_test['Assigned_Cluster'].unique()

    #     # Save clusters as JSON
    #     # script_dir = os.path.dirname(os.path.abspath(__file__))
    #     # cluster_json_path = os.path.join(script_dir, "X-test clusters.json")      
    #     # self.save_clusters_to_json(self, X_test, output_folder, feature)

    #     print("Clusters in training data:", train_clusters)
    #     print("Clusters assigned to test data:", test_clusters)

    #     # Ensure we have multiple clusters to evaluate the metrics
    #     if len(test_clusters) < 2:
    #         print("Not enough clusters to evaluate Silhouette Score or Davies-Bouldin Index.")
    #         return

    #     # Extract feature data for clustering evaluation
    #     feature_columns = [col for col in X_test.columns if col not in ['Assigned_Cluster', 'name']]
    #     X_features = X_test[feature_columns].values  # Convert to numpy array
    #     labels = X_test['Assigned_Cluster'].values

    #     # Compute Silhouette Score
    #     try:
    #         silhouette_avg = silhouette_score(X_features, labels)
    #         print(f"Silhouette Score: {silhouette_avg:.4f}")
    #     except ValueError:
    #         print("Silhouette Score could not be computed. Ensure more than one cluster exists.")

    #     # Compute Davies-Bouldin Index
    #     try:
    #         db_index = davies_bouldin_score(X_features, labels)
    #         print(f"Davies-Bouldin Index: {db_index:.4f}")
    #     except ValueError:
    #         print("Davies-Bouldin Index could not be computed. Ensure more than one cluster exists.")
