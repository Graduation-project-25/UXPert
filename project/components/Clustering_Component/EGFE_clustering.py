import json
import os
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
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
    

    def dbscan_cluster(self, feature):
        if feature == 'color':
            DBSCAN_dataset, clusters = self.dbscan_cluster_based_on_color_and_type()
        elif feature == 'position':
            DBSCAN_dataset, clusters = self.dbscan_cluster_based_on_position_and_type()
        elif feature == 'size':
            DBSCAN_dataset, clusters = self.dbscan_cluster_based_on_size_and_type()
        elif feature == 'screen_size':
            DBSCAN_dataset, clusters = self.dbscan_cluster_based_on_screen_size()
        return DBSCAN_dataset, clusters

    def dbscan_cluster_based_on_color_and_type(self):
        X_train = self.egfe_load_data.load_train_data()

        color_features = [col for col in X_train.columns if col.startswith('color_')]
        type_features =  [col for col in X_train.columns if col.startswith('type_')]
        X_train_selected = X_train[color_features + type_features]  

        #Remove null values
        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})

        # Apply DBSCAN
        clustering = DBSCAN(eps=0.2, min_samples=5).fit(X_train_selected)

        # Prepare the dataset with clusters
        DBSCAN_dataset = X_train_selected.copy()
        DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column
        #save cluster in json
        cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on Colors and type.json")      
        self.save_cluster_as_json(DBSCAN_dataset,cluster_json_path,'Cluster')
        print('Number of instances in each cluster\n',DBSCAN_dataset[['Cluster']].value_counts())  # View the number of instances in each cluster
        clusters = np.unique(clustering.labels_)
        return DBSCAN_dataset, clusters 
    
    def dbscan_cluster_based_on_size_and_type(self):
        X_train = self.egfe_load_data.load_train_data()

        size_features = ['width', 'height']
        type_features =  [col for col in X_train.columns if col.startswith('type_')]
        X_train_selected = X_train[size_features + type_features]

        #Remove null values
        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})

        # # Fit the DBSCAN model
        # clustering = DBSCAN(eps=0.1, min_samples=15).fit(X_train_selected)
        # To Enhance Accuracy
        # Fit Nearest Neighbors model
        nearest_neighbors = NearestNeighbors(n_neighbors=5)
        nearest_neighbors.fit(X_train_selected)
        distances, indices = nearest_neighbors.kneighbors(X_train_selected)
        distances = np.sort(distances[:, -1])        # Sort distances 

        # # Fit the DBSCAN model
        #0.95 , 8 -> 0.900
        optimal_eps = distances[int(len(distances) * 0.95)]  
        clustering = DBSCAN(eps=optimal_eps, min_samples=8).fit(X_train_selected)


        # Prepare the dataset with clusters
        DBSCAN_dataset = X_train_selected.copy()
        DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column
        #save cluster in json
        cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on size and type.json")      
        self.save_cluster_as_json(DBSCAN_dataset,cluster_json_path,'Cluster')
        print('Number of instances in each cluster\n',DBSCAN_dataset[['Cluster']].value_counts())  # View the number of instances in each cluster
        clusters = np.unique(clustering.labels_)
        return DBSCAN_dataset, clusters 

    def dbscan_cluster_based_on_position_and_type(self):
        X_train = self.egfe_load_data.load_train_data()
        size_features = ['position.x', 'position.y']
        type_features =  [col for col in X_train.columns if col.startswith('type_')]
        X_train_selected = X_train[size_features + type_features]
        #Remove null values
        if X_train_selected.isnull().any().any():
            X_train_selected = X_train_selected.fillna(0)
            X_train_selected = X_train_selected.astype({col: 'int' for col in X_train_selected.columns if col.startswith('type_')})

        # To Enhance Accuracy
        # Fit Nearest Neighbors model
        nearest_neighbors = NearestNeighbors(n_neighbors=5)
        nearest_neighbors.fit(X_train_selected)
        distances, indices = nearest_neighbors.kneighbors(X_train_selected)
        distances = np.sort(distances[:, -1])        # Sort distances 

        # # Fit the DBSCAN model
        optimal_eps = distances[int(len(distances) * 0.94)]  # 95th percentile distance
        clustering = DBSCAN(eps=optimal_eps, min_samples=10).fit(X_train_selected)

        # Prepare the dataset with clusters
        DBSCAN_dataset = X_train_selected.copy()
        DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column

        #save cluster in json
        cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on position and type.json")      
        self.save_cluster_as_json(DBSCAN_dataset,cluster_json_path,'Cluster')
        print('Number of instances in each cluster\n',DBSCAN_dataset[['Cluster']].value_counts())  # View the number of instances in each cluster
        clusters = np.unique(clustering.labels_)

        return DBSCAN_dataset, clusters 

    def dbscan_cluster_based_on_screen_size(self):
        X_train = self.egfe_load_data.load_train_data()
        X_train_selected = X_train[['screen_width', 'screen_height']]  
        print(X_train_selected)
        print(X_train_selected.columns)

        # Apply DBSCAN
        clustering = DBSCAN(eps=0.2, min_samples=10).fit(X_train_selected)

        # Prepare the dataset with clusters
        DBSCAN_dataset = X_train_selected.copy()
        DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column
        #save cluster in json
        cluster_json_path = os.path.join(self.output_folder, "X-train Clusters based on screen size.json")      
        self.save_cluster_as_json(DBSCAN_dataset,cluster_json_path,'Cluster')
        print('Number of instances in each cluster\n',DBSCAN_dataset[['Cluster']].value_counts())  # View the number of instances in each cluster
        clusters = np.unique(clustering.labels_)
        return DBSCAN_dataset, clusters 
    
    def save_cluster_as_json(self, clusters, cluster_json_path, group_by):
        clusters_dict = clusters.groupby(group_by).apply(lambda df: df.to_dict(orient='records'), include_groups=False).to_dict()
        with open(cluster_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(clusters_dict, json_file, indent=4, ensure_ascii=False)
    
    def handle_outliers(self, X_train, cluster_csv, outliers_csv):
        # Identify Outliers
        outliers = X_train[X_train['Cluster'] == -1]
        export_to_csv(X_train, cluster_csv)
        export_to_csv(outliers, outliers_csv)


#######################################################################################################
    def analyze_clusters(self, df):
        consistency_instance = HeuristicFactory.check_rule("consistency")
        cluster_groups = df.groupby('Cluster')
        cluster_analysis = []
        
        for cluster_id, group in cluster_groups:    
            num_elements = len(group)
            avg_width = group['width'].mean()
            avg_height = group['height'].mean()
            
            print(group.columns)
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



