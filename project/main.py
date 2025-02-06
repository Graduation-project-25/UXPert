import os
import sys
import json
import pandas as pd
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.Heuristics_Component.heuristic_rules.Consistency_using_clusters import ClusteringConsistency
from components.Heuristics_Component.heuristics_evaluation.minimalist_evaluation import MinimalistEvaluation
from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist
from components.Heuristics_Component.heuristic_rules.Consistency_using_clusters import ClusteringConsistency
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFE_ClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFE_ClusteringTesting
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Splitter_Component.json_data_splitter import JSONDataSplitter
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Visualizer_Component.EGFE_visualization import EGFE_Visualization


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

def main():
    dataset_folder = './data/raw/EGFE'
    image_folder = dataset_folder + '/images'
    json_folder = dataset_folder + '/jsons'
    output_folder = dataset_folder + '/extractedFeatures'
    train_folder = output_folder + '/train'
    test_folder = output_folder + '/test'
    evaluation_folder = output_folder + '/evaluation'

    os.makedirs(output_folder, exist_ok=True)

    # Initialize components
    egfe_ui_processing = EGFE_UiProcessing()
    egfe_ui_normalizing = EGFE_UiNormalizing()
    splitter = JSONDataSplitter(output_folder)
    egfe_clustering_evaluation = EGFE_ClusteringEvaluation()
    egfe_clustering = EGFE_Clustering(train_folder, output_folder)
    egfe_ui_extraction = EGFE_FeatureExtraction()
    egfe_visualization = EGFE_Visualization()
    egfe_clustering_testing = EGFE_ClusteringTesting()
    egfe_load_data = EGFE_LoadData()
    minimalist_evaluation = MinimalistEvaluation()

    # minimalist_evaluation.evaluate_rule(train_folder)




    # Step 1: Save json in extracted features folder
    # egfe_ui_processing.process_ui_elements(json_folder, output_folder)
    
    # Step 2: Split Data into Train and Test
    #splitter.save_split_files(train_folder, test_folder)
    
    # Step 3: Load Normalized train data
    # train_data = egfe_load_data.load_train_data()
    
    # Step 4: Visualize UI Elements (Scatter Plot)
    #egfe_visualization.scatter_plot_ui_elements(train_data)
    
    # Step 5: DBSCAN Clustering Based on selected feature
    clustered_data, clusters = egfe_clustering.dbscan_cluster('color')
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
    new_x_test = egfe_clustering_testing.assign_test_clusters(clustered_data,test_folder,'color')

    # print(new_x_test)
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
    # base_path = Path(__file__).resolve().parent  # Get current script directory
    # clusters_data_path = base_path / "data/raw/EGFE/extractedFeatures/X-train clusters.json"

    # with open(clusters_data_path, "r") as file:
    #     clusters_data = json.load(file)

    # minimalist_checker = Minimalist()
    # feedback = minimalist_checker.evaluate_rule(clusters_data)
    # for f in feedback:
    #     print(f)


    

    


    # clustering_instance = EGFE_Clustering(train_folder, output_folder)

    # # Run clustering for different features
    # features = ['color', 'position', 'size']
    # cluster_results = {}

    # for feature in features:
    #     print(f"Clustering based on {feature}...")
    #     DBSCAN_dataset, clusters = clustering_instance.dbscan_cluster(feature)
    #     cluster_results[feature] = DBSCAN_dataset  # Store clustering results
        
    # # Perform Consistency Analysis
    # for feature, df in cluster_results.items():
    #     print(df.head())  # Check first few rows

    # print(f"Analyzing consistency for {feature} clusters...")
    # clustering_instance.analyze_clusters()
        


    # data = {
    #     'Cluster': ['Cluster_1', 'Cluster_1', 'Cluster_2', 'Cluster_2', 'Cluster_3', 'Cluster_3'],
    #     'position.x': [1.1, 1.2, 5.0, 5.1, 10.5, 10.6],
    #     'position.y': [2.1, 2.2, 6.0, 6.1, 11.5, 11.6],
    #     'width': [100, 100, 200, 210, 300, 310],
    #     'height': [150, 150, 250, 260, 350, 340],
    #     'color_r': [0.1, 0.1, 0.5, 0.5, 0.9, 0.8],
    #     'color_g': [0.2, 0.2, 0.4, 0.3, 0.8, 0.9],
    #     'color_b': [0.3, 0.3, 0.3, 0.4, 0.7, 0.7]
    # }

    # df = pd.DataFrame(data)
    #clustered_test_data, _, _ = egfe_clustering.dbscan_cluster(test_folder)
    # Step 2: Create an instance of ClusteringConsistency
    # clustering_instance = EGFE_Clustering(train_folder, output_folder)

    # List of features to loop through
    # features_to_check = ['color', 'position', 'size', 'spacing']  # Added 'spacing' here

    # # Create an empty dictionary to store the reports
    # consistency_reports = {}

    # # Loop through the features and generate consistency reports
    # for feature in features_to_check:
    #     # Get the clustered data and clusters based on the feature
    #     clustered_data, clusters = clustering_instance.dbscan_cluster(feature)
    #     print(clustered_data.columns)
        
    #     # Check if the clustered data is not empty and generate consistency report
    #     if clustered_data is not None and not clustered_data.empty:
    #         consistency_instance = ClusteringConsistency(clustered_data)
    #         consistency_report = consistency_instance.generate_consistency_report()
            
    #         # Store the report in the dictionary
    #         consistency_reports[feature] = consistency_report

    # Print the final consistency report for all features
    # print("Cluster Consistency Reports:")
    # for feature, report in consistency_reports.items():
    #     print(f"Feature: {feature}")
    #     print(report)




        
if __name__ == "__main__":
    main()
#     print(f"Analyzing consistency for {feature} clusters...")
#     clustering_instance.analyze_clusters()




