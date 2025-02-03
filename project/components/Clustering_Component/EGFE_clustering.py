import json
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs
from sklearn.preprocessing import MinMaxScaler
from components.Feedback_Generator_Component.heuristics.consistency import Consistency
from components.Clustering_Component.clustering import ClusteringInterface
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from utils.csv_exporting import export_to_csv

class EGFEClustering(ClusteringInterface):    
    def __init__(self, train_folder,output_folder):
        self.output_folder = output_folder
        self.egfe_ui_processing = EGFE_UiProcessing()
        self.egfe_load_data = EGFE_LoadData(train_folder)
    

    def dbscan_cluster(self):
        X_train = self.egfe_load_data.load_train_data()
        print(X_train)
        print(X_train.columns)

        X_train=X_train[['width', 'height', 'position.x', 'position.y'] + 
                    [col for col in X_train.columns if col.startswith('color_')] + 
                    [col for col in X_train.columns if col.startswith('type_')]]

    # Clean data if necessary
        X_train = self.egfe_ui_processing.clean_data(X_train)
        print('X_train After cleaning:\n', X_train)

    # Fit the DBSCAN model
        clustering = DBSCAN(eps=0.5, min_samples=5).fit(X_train)

    # Prepare the dataset with clusters
        DBSCAN_dataset = X_train.copy()
        DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column
        print('DBSCAN_dataset:\n', DBSCAN_dataset)

        cluster_json_path = os.path.join(self.output_folder, "X-train clusters.json")      
        self.save_cluster_as_json(DBSCAN_dataset,cluster_json_path,'Cluster')

        points_in_each_cluster = DBSCAN_dataset.Cluster.value_counts().to_frame()
        print(points_in_each_cluster)
        clusters = np.unique(clustering.labels_)
    
        return DBSCAN_dataset, clusters

    def dbscan_cluster_based_on_color(self):
        X_train = self.egfe_load_data.load_train_data()
        print(X_train)
        print(X_train.columns)

        X_train = X_train[[col for col in X_train.columns if col.startswith('color_')]]


    # Clean data if necessary
        # X_train = self.egfe_ui_processing.clean_data(X_train)
        # print('X_train After cleaning:\n', X_train)

    # Fit the DBSCAN model
        dbscan = DBSCAN(eps=0.1, min_samples=5)
        clusters = dbscan.fit_predict(X_train)

        plt.scatter(X_train[:, X_train], X_train[:, 1], c=clusters, cmap='viridis', marker='o')
        plt.title("DBSCAN Clustering of Concentric Circles")
        plt.xlabel("color")
        plt.ylabel("Feature 1")
        plt.show()


    # Prepare the dataset with clusters
        # DBSCAN_dataset = X_train.copy()
        # DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column
        # print('DBSCAN_dataset:\n', DBSCAN_dataset)

        # cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on Colors.json")      
        # self.save_cluster_as_json(DBSCAN_dataset,cluster_json_path,'Cluster')

        # points_in_each_cluster = DBSCAN_dataset.Cluster.value_counts().to_frame()
        # print(points_in_each_cluster)
        # clusters = np.unique(clustering.labels_)
    
        # return DBSCAN_dataset, clusters

    def handle_outliers(self, X_train):
        # Identify Outliers
        outliers = X_train[X_train['Cluster'] == -1]
        export_to_csv(X_train, "cluster_assignments.csv")
        export_to_csv(outliers, "outliers.csv")


    def save_cluster_as_json(self, clusters, cluster_json_path, group_by):
        clusters_dict = clusters.groupby(group_by).apply(lambda df: df.to_dict(orient='records'), include_groups=False).to_dict()
        with open(cluster_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(clusters_dict, json_file, indent=4, ensure_ascii=False)
    
    def analyze_clusters(self, df):
        consistency_instance = HeuristicFactory.check_rule("consistency")
        cluster_groups = df.groupby('Cluster')
        cluster_analysis = []
        
        for cluster_id, group in cluster_groups:    
            num_elements = len(group)
            avg_width = group['width'].mean()
            avg_height = group['height'].mean()
            
            # Prevent division by zero in density calculation
            bbox_width = group['position.x'].max() - group['position.x'].min()
            bbox_height = group['position.y'].max() - group['position.y'].min()
            area = bbox_width * bbox_height if bbox_width > 0 and bbox_height > 0 else 1
            avg_density = num_elements / area  # Now safe from division by zero

            # Compute alignment consistency and heuristic consistency score
            alignment_consistency = consistency_instance.calculate_alignment_consistency(group)
            consistency_scores = consistency_instance.evaluate_rule(group)
            print("Factory pattern Testing, Consistency:", consistency_scores)
            
            # Store analysis
            cluster_analysis.append({
                "Cluster": cluster_id,
                "NumElements": num_elements,
                "AvgWidth": avg_width,
                "AvgHeight": avg_height,
                "AvgDensity": avg_density,
                "AlignmentConsistency": alignment_consistency,
                "TotalConsistency": consistency_scores,
            })
        
        return cluster_analysis
