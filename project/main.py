import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.model.evaluation import evaluate_clustering
from backend.model.testing import assign_test_clusters, evaluate_test_clusters
from backend.utils.EGFE_visualization import clustering_visualization_by_position, clustering_visulaization_by_size, scatter_plot_ui_elements,  visualize_alignment_consistency,visualize_color_consistency,visualize_size_proportionality, visualize_ui_elements
from backend.utils.RICO_visualization import visualize_rico_ui_elements
from backend.utils.EGFE_ui_extraction import  aggregate_ui_elements, extract_egfe_ui_elements, extract_json_file_path, split_dataset
from backend.utils.RICO_ui_extraction import extract_rico_ui_elements
from backend.utils.RICO_ui_extraction import extract_rico_ui_elements
from backend.model.EGFE_Clustering import analyze_clusters, dbscan_cluster, handle_outliers
from backend.heuristics.consistency import evaluate_consistency


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000) 


# from datasets import load_dataset

# # Load dataset from a local directory
# dataset = load_dataset("json", data_files="D:/Studying/Projects/Graduation/UXPert/project/data/raw/train_split_web70k.json")
# print(dataset)



dataset_folder = './data/raw/EGFE'  # Adjust the path if needed
# dataset_folder = './data/raw/RICO/unique_uis/combined'   # Extracting Rico (unique)
image_folder  = dataset_folder + '/images'  # Folder for images
json_folder  = dataset_folder + '/jsons'  # Folder for JSON files
output_folder = dataset_folder + '/extractedFeatures'
os.makedirs(output_folder, exist_ok=True)

def main():
    json_file_path = extract_json_file_path(json_folder,limit=10)

    ############################# EGFE Dataset #############################################

    # #extract ui elements 
    # elements, normalized_data = extract_egfe_ui_elements(json_file_path)  

    # # Aggregate by 'type'
    # aggregated_elements = aggregate_ui_elements(normalized_data)
    # print("Aggregated Elements:\n", aggregated_elements)
    # print("***************************************************************\n")

    # # Scatter plot of UI elements
    # scatter_plot_ui_elements(normalized_data)
    
    # # splitting dataset
    # X_train,X_test = split_dataset(normalized_data)
    # print("Training Data:\n", X_train)
    # print("Testing Data:\n", X_test)
    # print("***************************************************************\n")

    # # DBSCAN Clustering
    # X_train,DBSCAN_dataset, clusters = dbscan_cluster(X_train)
    # handle_outliers(X_train)
    # evaluate_clustering(DBSCAN_dataset)
    # analyze_clusters(DBSCAN_dataset)
    # clustering_visulaization_by_size(DBSCAN_dataset,clusters)
    # clustering_visualization_by_position(DBSCAN_dataset,clusters)
    # # visualize_alignment_consistency(DBSCAN_dataset)
    
    # visualize_color_consistency(DBSCAN_dataset)
    # visualize_size_proportionality(DBSCAN_dataset)
    # visualize_ui_elements(image_folder, json_folder, output_folder, limit=50)

    
    # print("#######################################################################################")

    # # Test data clustering
    # print("Clustering test data...")
    # clustered_test_data, _, _ = dbscan_cluster(X_test)

    # print("Evaluating test data clustering...")
    # evaluate_clustering(clustered_test_data)

    # # Assign test clusters
    # new_x_test = assign_test_clusters(DBSCAN_dataset, X_test, clusters)

    # # Evaluate test results
    # evaluate_test_clusters(new_x_test, DBSCAN_dataset)




    ############################# RICO Dataset #############################################

    dataset_folder = './project/data/raw/RICO/unique_uis/combined'   # Extracting Rico (unique)
    image_folder  = dataset_folder + '/images'  # Folder for images
    json_folder  = dataset_folder + '/jsons'  # Folder for JSON files
    output_folder = dataset_folder + '/extractedFeatures'
    os.makedirs(output_folder, exist_ok=True)

    rico_elements, rico_normalized_elements = extract_rico_ui_elements(json_file_path)  
    print(rico_normalized_elements)

    elements = extract_rico_ui_elements(json_file_path)

    # visualize_rico_ui_elements(image_folder, json_folder, output_folder, limit=50)

    
if __name__ == "__main__":
    main()
