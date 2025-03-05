import json
import os
import numpy as np
import pandas as pd
import hdbscan
from sklearn.cluster import DBSCAN
import hdbscan
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from components.Clustering_Component.clustering import ClusteringInterface
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from components.Heuristics_Component.heuristic_rules.Consistency_using_clusters import ClusteringConsistency
from utils.csv_exporting import export_to_csv
from database.cluster_repository import ClusterRepository
 
class EGFE_Clustering(ClusteringInterface):    
    def __init__(self, train_folder,output_folder, db):
        self.output_folder = output_folder
        self.train_folder = train_folder
        self.egfe_ui_processing = EGFE_UiProcessing()
        self.egfe_load_data = EGFE_LoadData()
        self.cluster_repository = ClusterRepository()
    

    def dbscan_cluster(self, feature):
        clustered_data = None
        clusters = None
        try:
            if feature == "color":
                clustered_data, clusters = self.hdbscan_cluster_based_on_color_and_type()
            elif feature == "position":
                clustered_data, clusters = self.hdbscan_cluster_based_on_position_and_type()
            elif feature == "size":
                clustered_data, clusters = self.hdbscan_cluster_based_on_size_and_type() 
            elif feature == "label":
                clustered_data, clusters = self.hdbscan_cluster_based_on_label_and_type() 
            # If clustering fails, raise an error
            if clustered_data is None or clusters is None:
                raise ValueError(f"Clustering failed for feature: {feature}")

        except Exception as e:
            print(f"Error in clustering for feature {feature}: {e}")
            clustered_data = pd.DataFrame()  # Return an empty DataFrame if clustering fails
            clusters = []

        return clustered_data, clusters
    
    def hdbscan_cluster_based_on_color_and_type(self):
        X_train = self.egfe_load_data.load_data(self.train_folder)
        color_features = [col for col in X_train.columns if col.startswith('color_')]
        type_features = [col for col in X_train.columns if col.startswith('type_')]
        X_train_selected = X_train[color_features + type_features]

        #Remove null values
        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})

        # Filter non-zero color rows
        mask = (X_train_selected[color_features] != 0).any(axis=1) | (X_train_selected[['color_r', 'color_g', 'color_b']].sum(axis=1) == 0)
        X_train_colored = X_train_selected[mask]
        print(f"Filtered to {len(X_train_colored)} rows with non-zero colors")

        # Cluster only colored data
        clustering = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=5, cluster_selection_epsilon=0.05).fit(X_train_colored)
        # Prepare the dataset with clusters
        clustered_data = X_train_colored.copy()
        clustered_data.loc[:, 'Cluster'] = clustering.labels_

        #save cluster in json
        # cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on Colors and type.json")
        # self.save_cluster_as_json(clustered_data, cluster_json_path, 'Cluster')
        print('Number of instances in each cluster\n', clustered_data[['Cluster']].value_counts())
        clusters = np.unique(clustering.labels_)

        # Save clusters in database
        self.cluster_repository.insert_cluster_data(clustered_data, "color")

        return clustered_data, clustering.labels_

    def hdbscan_cluster_based_on_size_and_type(self):
        X_train = self.egfe_load_data.load_data(self.train_folder)

        size_features = ['width', 'height']
        type_features = [col for col in X_train.columns if col.startswith('type_')]
        X_train_selected = X_train[size_features + type_features]

        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})

        # Feature Engineering (add before scaling)
        # Handle zero heights
        X_train_selected['aspect_ratio'] = X_train_selected.apply(
            lambda row: 0 if row['height'] == 0 else row['width'] / row['height'], axis=1
        )
        X_train_selected['area'] = X_train_selected['width'] * X_train_selected['height']

        # Scale size features
        scaler = StandardScaler()
        X_train_selected[['width', 'height', 'aspect_ratio', 'area']] = scaler.fit_transform(X_train_selected[['width', 'height', 'aspect_ratio', 'area']])

        # Filter non-zero size rows (adjust as needed)
        mask = (X_train_selected[['width','height']] != 0).any(axis=1) # only use width and height for the mask.
        X_train_sized = X_train_selected[mask]
        print(f"Filtered to {len(X_train_sized)} rows with non-zero sizes")

        # Cluster only sized data
        clustering = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=5, cluster_selection_epsilon=0.05).fit(X_train_sized)
        clustered_data = X_train_sized.copy()
        clustered_data.loc[:, 'Cluster'] = clustering.labels_

        # Print top cluster samples
        # print("Top cluster samples:")
        # unique_clusters = np.unique(clustering.labels_)
        # top_clusters = []
        # for cluster_id in unique_clusters:
        #     if cluster_id != -1:
        #         top_clusters.append((cluster_id,len(clustered_data[clustered_data['Cluster'] == cluster_id])))
        # top_clusters.sort(key=lambda x:x[1],reverse=True)
        # for cluster_id, size in top_clusters[:3]:
        #     sample = clustered_data[clustered_data['Cluster'] == cluster_id].head(2)
        #     print(f"Cluster {cluster_id} ({size}):")
        #     for row in sample.to_dict('records'):
        #         print(f"  Width: {row['width']}, Height: {row['height']} | Aspect Ratio: {row['aspect_ratio']} | Area: {row['area']} | Type: { {k: v for k, v in row.items() if k.startswith('type_') and v == 1}}")

        # cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on size and type.json")
        # self.save_cluster_as_json(clustered_data, cluster_json_path, 'Cluster')
        print('Number of instances in each cluster\n', clustered_data[['Cluster']].value_counts())
        clusters = np.unique(clustering.labels_)

        # Save clusters in database
        self.cluster_repository.insert_cluster_data(clustered_data, "size")

        return clustered_data, clustering.labels_

    def hdbscan_cluster_based_on_position_and_type(self):
        X_train = self.egfe_load_data.load_data(self.train_folder)
        position_features = ['position.x', 'position.y']
        type_features = [col for col in X_train.columns if col.startswith('type_')]
        X_train_selected = X_train[position_features + type_features]

        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})

        # Scale position features
        scaler = StandardScaler()
        X_train_selected[['position.x', 'position.y']] = scaler.fit_transform(X_train_selected[['position.x', 'position.y']])

        # Filter non-zero position rows
        mask = (X_train_selected[position_features] != 0).any(axis=1)
        X_train_positioned = X_train_selected[mask]
        print(f"Filtered to {len(X_train_positioned)} rows with non-zero positions")

        # Cluster only positioned data
        clustering = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=5, cluster_selection_epsilon=0.05).fit(X_train_positioned)
        clustered_data = X_train_positioned.copy()
        clustered_data.loc[:, 'Cluster'] = clustering.labels_

        # Print top cluster samples
        # print("Top cluster samples:")
        # unique_clusters = np.unique(clustering.labels_)
        # top_clusters = []
        # for cluster_id in unique_clusters:
        #     if cluster_id != -1:
        #         top_clusters.append((cluster_id, len(clustered_data[clustered_data['Cluster'] == cluster_id])))
        # top_clusters.sort(key=lambda x: x[1], reverse=True)
        # for cluster_id, size in top_clusters[:3]:
        #     sample = clustered_data[clustered_data['Cluster'] == cluster_id].head(2)
        #     print(f"Cluster {cluster_id} ({size}):")
        #     for row in sample.to_dict('records'):
        #         print(f"  Position X: {row['position.x']}, Position Y: {row['position.y']} | Type: { {k: v for k, v in row.items() if k.startswith('type_') and v == 1}}")

        # cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on position and type.json")
        # self.save_cluster_as_json(clustered_data, cluster_json_path, 'Cluster')
        print('Number of instances in each cluster\n', clustered_data[['Cluster']].value_counts())
        clusters = np.unique(clustering.labels_)
        
        # Save clusters in database
        self.cluster_repository.insert_cluster_data(clustered_data, "position")


        return clustered_data, clustering.labels_
        
    def hdbscan_cluster_based_on_label_and_type(self):
        X_train = self.egfe_load_data.load_data(self.train_folder)
        type_features = [col for col in X_train.columns if col.startswith('type_')]
        label_feature = ['labeled']
        size_features = ['width', 'height']
        X_train_selected = X_train[size_features + type_features + label_feature]

        #Remove null values
        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})
        
        #Remove duplicates
        X_train_selected = X_train_selected.drop_duplicates()

        # # Fit the DBSCAN model
        clustering = hdbscan.HDBSCAN(
                min_samples=20,                
                cluster_selection_epsilon=0.5
            ).fit(X_train_selected)

        # Prepare the dataset with clusters
        clustered_data = X_train_selected.copy()
        clustered_data['Cluster'] = clustering.labels_  # Add cluster labels        
                
        # cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on label and type.json")      
        # self.save_cluster_as_json(clustered_data,cluster_json_path,'Cluster')
        print('Number of instances in each cluster\n',clustered_data[['Cluster']].value_counts())  # View the number of instances in each cluster
        clusters = np.unique(clustering.labels_)

        # Save clusters in database
        self.cluster_repository.insert_cluster_data(clustered_data, "label")

        return clustered_data, clustering.labels_ 

    
    def save_cluster_as_json(self, clusters, cluster_json_path, group_by):
        clusters_dict = clusters.groupby(group_by).apply(lambda df: df.to_dict(orient='records'), include_groups=False).to_dict()
        with open(cluster_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(clusters_dict, json_file, indent=4, ensure_ascii=False)
    
    def handle_outliers(self, X_train, cluster_csv, outliers_csv):
        # Identify Outliers
        outliers = X_train[X_train['Cluster'] == -1]
        export_to_csv(X_train, cluster_csv)
        export_to_csv(outliers, outliers_csv)

    def analyze_clusters(self):
        report = {}
        # Define which features need consistency checking
        features_to_check = ['color', 'position', 'size', 'screen_size']

        for feature in features_to_check:
            dbscan_dataset, clusters = self.dbscan_cluster(feature)

            if dbscan_dataset is not None and not dbscan_dataset.empty:
                consistency_instance = ClusteringConsistency(dbscan_dataset)
                report[feature] = consistency_instance.generate_consistency_report()

        print("Cluster Consistency Report:", report)
        return report
    

