import os
import sys
import json
import pandas as pd
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFE_ClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFE_ClusteringTesting
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Splitter_Component.json_data_splitter import JSONDataSplitter
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Feedback_Generator_Component.heuristics.mini import Minimalist
from components.Visualizer_Component.EGFE_visualization import EGFE_Visualization
from components.Feedback_Generator_Component.heuristics.consistency import Consistency
from components.Clustering_Component.EGFE_heuristic_evaluation import EGFE_HeuristicEvaluation


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

def main():
    dataset_folder = './data/raw/EGFE'
    image_folder = dataset_folder + '/images'
    json_folder = dataset_folder + '/jsons'
    output_folder = dataset_folder + '/extractedFeatures'
    train_folder = output_folder + '/train'
    test_folder = output_folder + '/test'
    os.makedirs(output_folder, exist_ok=True)

    # Initialize components
    egfe_ui_processing = EGFE_UiProcessing()
    egfe_ui_normalizing = EGFE_UiNormalizing()
    splitter = JSONDataSplitter(output_folder)
    egfe_clustering_evaluation = EGFE_ClusteringEvaluation()
    egfe_clustering = EGFE_Clustering(train_folder, output_folder)
    egfe_ui_extraction = EGFE_FeatureExtraction()
    egfe_visualization = EGFE_Visualization()
    egfe_clustering_testing = EGFE_ClusteringTesting(train_folder)
    egfe_load_data = EGFE_LoadData(train_folder)
    # screen_size_cluster_file = output_folder + '/X-train Clusters based on screen size.json'
    egfe_heuristic_evaluation = EGFE_HeuristicEvaluation()

    egfe_heuristic_evaluation.evaluate_minimalist_on_designs(train_folder)




    # Step 1: Save json in extracted features folder
    # egfe_ui_processing.process_ui_elements(json_folder, output_folder)
    
    # Step 2: Split Data into Train and Test
    # splitter.save_split_files(train_folder, test_folder)
    
    # Step 3: Load Normalized train data
    # train_data = egfe_load_data.load_train_data()
    
    # Step 4: Visualize UI Elements (Scatter Plot)
    # egfe_visualization.scatter_plot_ui_elements(train_data)
    
    # Step 5: DBSCAN Clustering Based on selected feature
    # clustered_data, clusters = egfe_clustering.dbscan_cluster('color')
    # clustered_data, clusters = egfe_clustering.handle_outliers(clustered_data, "Color Clustering", "Color Clustering Outliers")
    # egfe_clustering_evaluation.evaluate_clustering(data_to_evaluate)



    ##############################################################################################################
    
    # Step 6: Visualizing Clustering Results
    # egfe_visualization.clustering_visualization_by_size(clustered_data, clusters)
    # egfe_visualization.clustering_visualization_by_position(clustered_data, clusters)
    # egfe_visualization.visualize_alignment_consistency(clustered_data)
    # egfe_visualization.visualize_color_consistency(clustered_data)
    # egfe_visualization.visualize_size_proportionality(clustered_data)
    
    # Step 7: Test Data Clustering
    # clustered_test_data, _, _ = egfe_clustering.dbscan_cluster(test_folder)
    # egfe_clustering_evaluation.evaluate_clustering(clustered_test_data)
    
    # Step 8: Assign Clusters to Test Data
    # new_x_test = egfe_clustering_testing.assign_test_clusters(clustered_data, test_folder, clusters)
    # egfe_clustering_testing.evaluate_test_clusters(new_x_test, clustered_data)
    
    # Step 9: Minimalist Heuristic Evaluation
    # element_count, status = minimalist.count_ui_elements(clustered_data)
    # print("Number of elements =", element_count)
    # print("Status of the elements =", status)

    ##############################################################################################

    # base_path = Path(_file_).resolve().parent  # Get current script directory
    # file_path = base_path / "data/raw/EGFE/extractedFeatures/X-train clusters.json"

    # if not file_path.exists():
    #     raise FileNotFoundError(f"File not found: {file_path}")

    # evaluator = EGFE_HeuristicEvaluation(str(file_path))
    # # evaluation_results = evaluator.evaluate_minimalist_on_clusters()
    # evaluator.evaluate_minimalist()
    # print(evaluator.evaluate_minimalist())

    # clusters_data = "project/data/raw/EGFE/extractedFeatures/X- train clusters.json"

    # clusters_data_path = "project/data/raw/EGFE/extractedFeatures/X-train clusters.json"
    # base_path = Path(_file_).resolve().parent  # Get current script directory
    # clusters_data_path = base_path / "data/raw/EGFE/extractedFeatures/X-train clusters.json"

    # with open(clusters_data_path, "r") as file:
    #     clusters_data = json.load(file)

    # minimalist_checker = Minimalist(clusters_data)
    # feedback = minimalist_checker.evaluate_rule()
    # for f in feedback:
    #     print(f)



    clustering_instance = EGFE_Clustering(train_folder, output_folder)

    # Run clustering for different features
    features = ['color', 'position', 'size']
    cluster_results = {}

    for feature in features:
        print(f"Clustering based on {feature}...")
        DBSCAN_dataset, clusters = clustering_instance.dbscan_cluster(feature)
        cluster_results[feature] = DBSCAN_dataset  # Store clustering results
        
    # Perform Consistency Analysis
    for feature, df in cluster_results.items():
        print(df.head())  # Check first few rows

        print(f"Analyzing consistency for {feature} clusters...")
        clustering_instance.analyze_clusters()
    if __name__ == "__main__":
        main()


