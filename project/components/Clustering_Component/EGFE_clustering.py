import json
import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from components.Feedback_Generator_Component.heuristics.consistency import Consistency
from components.Clustering_Component.clustering import ClusteringInterface
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from utils.csv_exporting import export_to_csv

class EGFEClustering(ClusteringInterface):    
    def __init__(self, train_folder,output_folder):
        self.train_folder = train_folder
        self.output_folder = output_folder
        self.egfe_ui_normalizing = EGFE_UiNormalizing()
        self.egfe_ui_processing = EGFE_UiProcessing()

    def load_train_data(self):
        """Load and merge all JSON files from the training folder into a DataFrame."""
        all_data = []
        
        for file_name in os.listdir(self.train_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.train_folder, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # get_all_normalized_json_files(self.train_folder)
                    df = pd.json_normalize(data["elements"])  # Extract UI elements
                    df["file_name"] = file_name  # Track file origin
                    all_data.append(df)
        if not all_data:
            raise ValueError("No JSON files found in the training folder.")
        return pd.concat(all_data, ignore_index=True)
    

    def dbscan_cluster(self, X_train):
        # X_train = self.load_train_data()

        X_train=X_train[['width', 'height', 'position.x', 'position.y'] + 
                    [col for col in X_train.columns if col.startswith('color_')] + 
                    [col for col in X_train.columns if col.startswith('type_')]]

        X_train = self.egfe_ui_processing.clean_data(X_train)

        print('New X_train\n', X_train)


        # Fit the DBSCAN model
        clustering = DBSCAN(eps=0.5, min_samples=5).fit(X_train)

        # Assign cluster labels to each design
        X_train['Cluster'] = clustering.labels_

        # Prepare the the dataset with clusters 
        DBSCAN_dataset = X_train.copy()
        DBSCAN_dataset.loc[:,'Cluster'] = clustering.labels_  # adding cluster column

        cluster_json_path = os.path.join(self.output_folder, "X-train clusters.json")      
        self.save_cluster_as_json(X_train,cluster_json_path,'Cluster')

        points_in_each_cluster = DBSCAN_dataset.Cluster.value_counts().to_frame()
        print(points_in_each_cluster)
        clusters = np.unique(clustering.labels_)
        
        return X_train, DBSCAN_dataset, clusters



    def handle_outliers(self,X_train):
        # Identify Outliers
        outliers = X_train[X_train['Cluster'] == -1]

        # Save the cluster assignments and outliers
        export_to_csv(X_train, "cluster_assignments.csv")
        export_to_csv(outliers, "outliers.csv")

    def save_cluster_as_json(self,clusters,cluster_json_path, group_by):
        clusters_dict = clusters.groupby(group_by).apply(lambda df: df.to_dict(orient='records'), include_groups=False).to_dict()
        with open(cluster_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(clusters_dict, json_file, indent=4, ensure_ascii=False) 

    def analyze_clusters(self,df):
        consistency = Consistency()
        consistency_instance = HeuristicFactory.check_rule("consistency")

        # Group by cluster
        cluster_groups = df.groupby('Cluster')

        cluster_analysis = []
        for cluster_id, group in cluster_groups:    
            # Calculate metrics for the cluster
            num_elements = len(group)
            avg_width = group['width'].mean()
            avg_height = group['height'].mean()
            avg_density = num_elements / ((group['position.x'].max() - group['position.x'].min()) *
                                        (group['position.y'].max() - group['position.y'].min()))
            alignment_consistency = consistency.calculate_alignment_consistency(group)
            consistency_scores = consistency_instance.evaluate_rule(group)
            print("Factory pattern Testing, Consistency" , consistency_scores)

            # Store analysis
            cluster_analysis.append({
                "Cluster": cluster_id,
                "NumElements": num_elements,
                "AvgWidth": avg_width,
                "AvgHeight": avg_height,
                "AvgDensity": avg_density,
                "AlignmentConsistency": alignment_consistency,
                "TotalConsistency" : [consistency_scores],
            })

            # df = df.merge(analysis_df[['Cluster', 'TotalConsistency']], on='Cluster', how='left')
    
            
        # Convert to Dataframe for better visualization
        # analysis_df = pd.DataFrame(cluster_analysis)

        # print("Cluster Analysis:\n", analysis_df)

        # export_to_csv(analysis_df, "cluster_analysis.csv")

        # return analysis_df
