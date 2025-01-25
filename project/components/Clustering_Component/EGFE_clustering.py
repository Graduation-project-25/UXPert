import json
import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics import davies_bouldin_score, silhouette_score

from components.Feedback_Generator_Component.heuristics.consistency import evaluate_consistency
from utils.csv_exporting import export_to_csv


def dbscan_cluster(X_train):
    X_train=X_train[['width', 'height', 'position.x', 'position.y'] + 
                 [col for col in X_train.columns if col.startswith('color_')] + 
                 [col for col in X_train.columns if col.startswith('type_')]]
    print('New X_train\n', X_train)

    # Fit the DBSCAN model
    clustering = DBSCAN(eps=0.5, min_samples=5).fit(X_train)

    # Assign cluster labels to each design
    X_train['Cluster'] = clustering.labels_

    # Prepare the the dataset with clusters 
    DBSCAN_dataset = X_train.copy()
    DBSCAN_dataset.loc[:,'Cluster'] = clustering.labels_  # adding cluster column

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cluster_json_path = os.path.join(script_dir, "X-train clusters.json")      
    save_cluster_as_json(X_train,cluster_json_path,'Cluster')

    points_in_each_cluster = DBSCAN_dataset.Cluster.value_counts().to_frame()
    print(points_in_each_cluster)
    clusters = np.unique(clustering.labels_)
    

    return X_train, DBSCAN_dataset, clusters

def handle_outliers(X_train):
    # Identify Outliers
    outliers = X_train[X_train['Cluster'] == -1]

    # Save the cluster assignments and outliers
    export_to_csv(X_train, "cluster_assignments.csv")
    export_to_csv(outliers, "outliers.csv")

def save_cluster_as_json(clusters,cluster_json_path, group_by):
   clusters_dict = clusters.groupby(group_by).apply(lambda df: df.to_dict(orient='records'), include_groups=False).to_dict()
   with open(cluster_json_path, 'w', encoding='utf-8') as json_file:
       json.dump(clusters_dict, json_file, indent=4, ensure_ascii=False)

def calculate_alignment_consistency(group):
    # This measures how well elements are aligned either horizontally or vertically.
    x_positions = group['position.x'].values
    y_positions = group['position.y'].values

    # Check horizontal and vertical alignment variance
    horizontal_alignment = np.var(x_positions)
    vertical_alignment = np.var(y_positions)

    # Consistency is inversely proportional to alignment variance
    alignment_consistency = 1 / (1 + horizontal_alignment + vertical_alignment)
    return alignment_consistency

def analyze_clusters(df):
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
        alignment_consistency = calculate_alignment_consistency(group)
        consistency_scores = evaluate_consistency(group)
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
    analysis_df = pd.DataFrame(cluster_analysis)

    print("Cluster Analysis:\n", analysis_df)

    export_to_csv(analysis_df, "cluster_analysis.csv")

    return analysis_df
