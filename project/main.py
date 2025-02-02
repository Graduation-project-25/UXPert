import os
import sys
import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.Feature_Extractor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Clustering_Component.EGFE_clustering import EGFEClustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFEClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFEClusteringTesting
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Visualizer_Component.EGFE_visualization import EGFE_Visualization

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000) 
dataset_folder = './data/raw/EGFE'
image_folder  = dataset_folder + '/images'  
json_folder  = dataset_folder + '/jsons' 
output_folder = dataset_folder + '/extractedFeatures'
os.makedirs(output_folder, exist_ok=True)

def main():
    egfe_clustering = EGFEClustering()
    egfe_clustering_evaluation = EGFEClusteringEvaluation()
    egfe_clustering_testing = EGFEClusteringTesting()
    egfe_ui_extraction = EGFE_FeatureExtraction()
    egfe_ui_processing = EGFE_UiProcessing()
    egfe_visualization = EGFE_Visualization()

    json_file_path = egfe_ui_extraction.extract_json_file_path(json_folder,limit=10)

    ############################# EGFE Dataset #############################################

    # extract ui elements 
    elements, normalized_data = egfe_ui_extraction.extract_ui_elements(json_file_path) 

    #save json in extracted features
    # egfe_ui_processing.process_ui_elements(json_folder, output_folder)

    # Aggregate by 'type'
    aggregated_elements = egfe_ui_extraction.aggregate_ui_elements(normalized_data)
    print("Aggregated Elements:\n", aggregated_elements)
    print("***************************************************************\n")

    # Scatter plot of UI elements
    egfe_visualization.scatter_plot_ui_elements(normalized_data)
    
    # splitting dataset
    X_train,X_test = egfe_ui_extraction.split_dataset(normalized_data)
    print("Training Data:\n", X_train)
    print("Testing Data:\n", X_test)
    print("***************************************************************\n")

    # DBSCAN Clustering
    X_train,DBSCAN_dataset, clusters = egfe_clustering.dbscan_cluster(X_train)
    egfe_clustering.handle_outliers(X_train)
    egfe_clustering_evaluation.evaluate_clustering(DBSCAN_dataset)
    egfe_clustering.analyze_clusters(DBSCAN_dataset)
    egfe_visualization.clustering_visualization_by_size(DBSCAN_dataset,clusters)
    egfe_visualization.clustering_visualization_by_position(DBSCAN_dataset,clusters)
    egfe_visualization.visualize_alignment_consistency(DBSCAN_dataset)
    egfe_visualization.visualize_color_consistency(DBSCAN_dataset)
    egfe_visualization.visualize_size_proportionality(DBSCAN_dataset)


    # #visualize ui elements
    # egfe_visualization.visualize_ui_elements(image_folder, json_folder, output_folder, limit=50)

    # print("#######################################################################################")

    # Test data clustering
    print("Clustering test data...")
    clustered_test_data, _, _ = egfe_clustering.dbscan_cluster(X_test)

    print("Evaluating test data clustering...")
    egfe_clustering_evaluation.evaluate_clustering(clustered_test_data)

    # Assign test clusters
    new_x_test = egfe_clustering_testing.assign_test_clusters(DBSCAN_dataset, X_test, clusters)

    # Evaluate test results
    egfe_clustering_testing.evaluate_test_clusters(new_x_test, DBSCAN_dataset)


  

    ############################# RICO Dataset #############################################

    # dataset_folder = './project/data/raw/RICO/unique_uis/combined'   # Extracting Rico (unique)
    # image_folder  = dataset_folder + '/images'  # Folder for images
    # json_folder  = dataset_folder + '/jsons'  # Folder for JSON files
    # output_folder = dataset_folder + '/extractedFeatures'
    # os.makedirs(output_folder, exist_ok=True)

    # rico_elements, rico_normalized_elements = extract_rico_ui_elements(json_file_path)  
    # print(rico_normalized_elements)

    # elements = extract_rico_ui_elements(json_file_path)

    # visualize_rico_ui_elements(image_folder, json_folder, output_folder, limit=50)

    
if __name__ == "__main__":
    main()
