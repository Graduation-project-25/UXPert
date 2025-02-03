import json
import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from components.Feedback_Generator_Component.heuristics.consistency import Consistency
from components.Clustering_Component.clustering import ClusteringInterface
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from utils.csv_exporting import export_to_csv

class EGFEClustering(ClusteringInterface):    
    def __init__(self, train_folder,output_folder):
        self.scale = MinMaxScaler()
        self.train_folder = train_folder
        self.output_folder = output_folder
        self.egfe_ui_normalizing = EGFE_UiNormalizing()
        self.egfe_ui_processing = EGFE_UiProcessing()
        self.egfe_ui_extraction = EGFE_FeatureExtraction()

    def load_train_data(self):
        """Load and merge all JSON files from the training folder into a DataFrame."""
        all_data = []
        
        for file_name in os.listdir(self.train_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.train_folder, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        if "elements" not in data:
                            print(f"Warning: 'elements' key missing in {file_name}. Skipping file.")
                            continue

                        # df1 = pd.json_normalize(data["screen_size"])  # Extract UI elements
                        # print(df1)


                        # Extract screen dimensions (if available)
                        # screen_width = data.get("screen_width", 0)
                        # screen_height = data.get("screen_height", 0)

                        # Add screen dimensions
                        # df["screen_width"] = screen_width
                        # df["screen_height"] = screen_height
                        # df["file_name"] = file_name  # Track file origin

                        #Normalize screen size
                        # Y = df[['screen_width', 'screen_height']]
                        # df[['screen_width', 'screen_height']] = self.scale.fit_transform(Y)

                        df = self.egfe_ui_normalizing.normalize_ui_elements(data["elements"])

                            
                        all_data.append(df)

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing {file_name}: {e}. Skipping file.")

        if not all_data:
            raise ValueError("No JSON files found in the training folder.")
        
        return pd.concat(all_data, ignore_index=True)
    

    
    def dbscan_cluster(self):
        X_train = self.load_train_data()
        print(X_train)
        print(X_train.columns)

        X_train=X_train[['width', 'height', 'position.x', 'position.y'] + 
                    [col for col in X_train.columns if col.startswith('color_')] + 
                    [col for col in X_train.columns if col.startswith('type_')]]
                    
                        # #normalize type
        # X_train = pd.get_dummies(X_train, columns=['type'], prefix='type')  # One-hot encode the 'type' column
        # X_train = X_train.astype({col: 'int' for col in X_train.columns if col.startswith('type_')})  # Convert Boolean columns to 0 and 1


        X_train = self.egfe_ui_processing.clean_data(X_train)
        print('New X_train\n', X_train)

        # Fit the DBSCAN model
        clustering = DBSCAN(eps=0.5, min_samples=5).fit(X_train)
        X_train['Cluster'] = clustering.labels_

        # Prepare dataset with clusters
        DBSCAN_dataset = X_train.copy()
        DBSCAN_dataset.loc[:, 'Cluster'] = clustering.labels_  # Adding cluster column

        cluster_json_path = os.path.join(self.output_folder, "X-train clusters.json")      
        # self.save_cluster_as_json(X_train,cluster_json_path,'Cluster')

        points_in_each_cluster = DBSCAN_dataset.Cluster.value_counts().to_frame()
        print(points_in_each_cluster)
        clusters = np.unique(clustering.labels_)
        
        return X_train, DBSCAN_dataset, clusters




    def handle_outliers(self,X_train):
        # Identify Outliers
        outliers = X_train[X_train['Cluster'] == -1]
        export_to_csv(X_train, "cluster_assignments.csv")
        export_to_csv(outliers, "outliers.csv")


    def save_cluster_as_json(self,clusters,cluster_json_path, group_by):
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
