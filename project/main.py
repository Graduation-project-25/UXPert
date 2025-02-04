import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFE_ClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFE_ClusteringTesting
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Splitter_Component.json_data_splitter import JSONDataSplitter
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
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
    minimalist = Minimalist()

    # Step 1: Process UI Elements
    # egfe_ui_processing.process_ui_elements(json_folder, output_folder)
    
    # Step 2: Split Data into Train and Test
    # splitter.save_split_files(train_folder, test_folder)
    
    # Step 3: Normalize Data
    # train_data = egfe_ui_processing.convert_json_to_dataframe(train_folder)
    # normalized_elements, normalized_screen_size = egfe_ui_normalizing.get_normalized_data(train_data)
    
    # Step 4: Visualize UI Elements (Scatter Plot)
    # egfe_visualization.scatter_plot_ui_elements(normalized_elements)
    
    # Step 5: Clustering (DBSCAN Based on Screen Size)
    clustered_data, data_to_evaluate, clusters = egfe_clustering.dbscan_cluster('screen_size')
    egfe_clustering_evaluation.evaluate_clustering(data_to_evaluate)
    
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
    
if __name__ == "__main__":
    main()
