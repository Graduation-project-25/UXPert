import os
import numpy as np
from scipy.spatial.distance import cdist

from components.Clustering_Component.clustering_testing import ClusteringTestingInterface
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData


class EGFE_ClusteringTesting(ClusteringTestingInterface):
    def __init__(self):
        self.data_loader = EGFE_LoadData()
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

    def assign_test_clusters(self, train_folder, X_test, feature):
        # Load training data
        X_train = self.data_loader.load_data(train_folder)

        # Select features based on the given feature type
        if feature == "color":
            selected_features = [col for col in X_train.columns if col.startswith('color_')] + \
                                [col for col in X_train.columns if col.startswith('type_')]
        elif feature == "size":
            selected_features = ['width', 'height'] + \
                                [col for col in X_train.columns if col.startswith('type_')]
        elif feature == "position":
            selected_features = ['position.x', 'position.y'] + \
                                [col for col in X_train.columns if col.startswith('type_')]
        else:
            raise ValueError("Invalid feature type. Choose from 'color', 'size', or 'position'.")

        # Extract the relevant features for training and test data
        X_train_selected = X_train[selected_features]
        X_test_selected = X_test[selected_features]

        # Compute cluster centers from training data
        unique_clusters = X_train['Cluster'].unique()
        cluster_centers = {
            cluster: X_train_selected[X_train['Cluster'] == cluster].mean(axis=0) 
            for cluster in unique_clusters
        }

        # Convert to numpy arrays for distance computation
        test_features = X_test_selected.values
        cluster_centers_array = np.array(list(cluster_centers.values()))

        # Compute distances and assign clusters
        distances = cdist(test_features, cluster_centers_array)
        assigned_clusters = distances.argmin(axis=1)
        
        # Assign clusters to X_test
        X_test['Assigned_Cluster'] = assigned_clusters

        return X_test



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

    def evaluate_test_clusters(self,X_test, X_train):
        # Compare cluster consistency or use metrics like silhouette scores
        train_clusters = X_train['Cluster'].unique()
        test_clusters = X_test['Assigned_Cluster'].unique()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        cluster_json_path = os.path.join(script_dir, "X-test clusters.json")      
        self.egfe_clustering.save_cluster_as_json(X_test,cluster_json_path,'Assigned_Cluster')


        print("Clusters in training data:", train_clusters)
        print("Clusters assigned to test data:", test_clusters)
