import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFE_ClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFE_ClusteringTesting
from components.Clustering_Component.EGFE_heuristic_evaluation import EGFE_HeuristicEvaluation
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Splitter_Component.json_data_splitter import JSONDataSplitter
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
from components.Visualizer_Component.EGFE_visualization import EGFE_Visualization

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000) 


dataset_folder = './data/raw/EGFE'
image_folder  = dataset_folder + '/images'  
json_folder  = dataset_folder + '/jsons' 
output_folder = dataset_folder + '/extractedFeatures'
train_folder = output_folder + '/train'
test_folder = output_folder + '/test'
os.makedirs(output_folder, exist_ok=True)

def main():

    ############################# EGFE Dataset #############################################
    egfe_ui_processing = EGFE_UiProcessing()
    egfe_ui_normalizing = EGFE_UiNormalizing()
    splitter = JSONDataSplitter(output_folder)
    egfe_clustering_evaluation = EGFE_ClusteringEvaluation()
    egfe_clustering = EGFE_Clustering(train_folder,output_folder)
    egfe_ui_extraction = EGFE_FeatureExtraction()
    egfe_visualization = EGFE_Visualization()
    egfe_clustering_testing = EGFE_ClusteringTesting(train_folder)
    egfe_load_data = EGFE_LoadData(train_folder)
    minimalist = Minimalist()

    # screen_size_cluster_file = output_folder + '/X-train Clusters based on screen size.json'
    egfe_heuristic_evaluation = EGFE_HeuristicEvaluation()

    # X_train = egfe_load_data.load_train_data()

    # save json in extracted features folder
    # egfe_ui_processing.process_ui_elements(json_folder, output_folder)


    # splitting to test and train
    # splitter.save_split_files(train_folder, test_folder)

    # Normalization
    # train_data = egfe_ui_processing.convert_json_to_dataframe(train_folder)
    # normalized_elements, normalized_screen_size = egfe_ui_normalizing.get_normalized_data(train_data)


    # Scatter plot of UI elements
    # egfe_visualization.scatter_plot_ui_elements(normalized_data)
    

    #############################################################################
    # DBSCAN Clustering
    # clustered_data, clusters = egfe_clustering.dbscan_cluster('color')
    # egfe_clustering.handle_outliers(egfe_clustering,"screen_size_cluster_assignments.csv","screen_size_outliers.csv")
    # egfe_clustering_evaluation.evaluate_clustering(egfe_clustering)



    #############################################################################
    # Rule Evaluation
    # egfe_heuristic_evaluation.evaluate_minimalist_on_designs(train_folder)
    # egfe_heuristic_evaluation.evaluate_heuristics()





    #################################################################################
    # analysis_results = egfe_clustering.analyze_clusters(DBSCAN_dataset)
    # egfe_visualization.clustering_visualization_by_size(DBSCAN_dataset,clusters)
    # egfe_visualization.clustering_visualization_by_position(DBSCAN_dataset,clusters)
    # egfe_visualization.visualize_alignment_consistency(DBSCAN_dataset)
    # egfe_visualization.visualize_color_consistency(DBSCAN_dataset)
    # egfe_visualization.visualize_size_proportionality(DBSCAN_dataset)
    # egfe_visualization.clustering_visualization_by_size(DBSCAN_dataset,clusters)
    # egfe_visualization.clustering_visualization_by_position(DBSCAN_dataset,clusters)
    # egfe_visualization.visualize_alignment_consistency(DBSCAN_dataset)
    # egfe_visualization.visualize_color_consistency(DBSCAN_dataset)
    # egfe_visualization.visualize_size_proportionality(DBSCAN_dataset)


    ## Visualize ui elements
    # egfe_visualization.visualize_ui_elements(image_folder, json_folder, output_folder, limit=50)

    # print("#######################################################################################")

    # # Test data clustering
    # print("Clustering test data...")
    # clustered_test_data, _, _ = egfe_clustering.dbscan_cluster(X_test)

    # print("Evaluating test data clustering...")
    # egfe_clustering_evaluation.evaluate_clustering(clustered_test_data)

    # # Assign test clusters
    # new_x_test = egfe_clustering_testing.assign_test_clusters(DBSCAN_dataset, X_test, clusters)

    # # Evaluate test results
    # egfe_clustering_testing.evaluate_test_clusters(new_x_test, DBSCAN_dataset)

    # print(type(DBSCAN_dataset))
    # print(DBSCAN_dataset.head() if isinstance(DBSCAN_dataset, pd.DataFrame) else DBSCAN_dataset)




    # Test Minimalist
    # element_count, status = minimalist.count_ui_elements(DBSCAN_dataset)
    # print("Number of elements = ", element_count)
    # print("Status of the elements = ", status)

  

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


