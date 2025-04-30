import json
import os
import sys
import pandas as pd

# Database trial
from pymongo import MongoClient
from database.cluster_repository import ClusterRepository



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.Heuristics_Component.minimalist import Minimalist
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Clustering_Component.EGFE_clustering_evaluation import EGFE_ClusteringEvaluation
from components.Clustering_Component.EGFE_clustering_testing import EGFE_ClusteringTesting
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData
from components.Data_Processor_Component.EGFE_ui_normalizing import EGFE_UiNormalizing
from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Splitter_Component.json_data_splitter import JSONDataSplitter
from components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction
from components.Heuristics_Component.heuristic_factory import HeuristicFactory
from components.Visualizer_Component.EGFE_visualization import EGFE_Visualization

from PIL import Image, ImageDraw

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

dataset_folder = './data/raw/EGFE'
image_folder = dataset_folder + '/images'
json_folder = dataset_folder + '/jsons'
output_folder = dataset_folder + '/extractedFeatures'
train_folder = output_folder + '/train'
test_folder = output_folder + '/test'
evaluation_folder = output_folder + '/evaluation'

os.makedirs(output_folder, exist_ok=True)

def main():
    
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
    recognition_instance = HeuristicFactory.check_rule("recognition")

    # Image Generation Test
    # Define file paths
    # json_file_path = "figma_features/extracted/design_4.json"
    # output_image_path = "figma_features/extracted/0testtttt.png"

    # # Load JSON data from the file
    # with open(json_file_path, "r", encoding="utf-8") as file:
    #     json_data = json.load(file)
    #     print(json_data)

    #     # Extract screen dimensions
    #     screen_width = json_data["screen_size"]["screen_width"]
    #     screen_height = json_data["screen_size"]["screen_height"]

    #     # Create a blank white canvas
    #     image = Image.new("RGB", (screen_width, screen_height), "white")
    #     draw = ImageDraw.Draw(image)

    #     # Process and draw each UI element
    #     for element in json_data["elements"]:
    #         x = element["position.x"]
    #         y = element["position.y"]
    #         width = element["width"]
    #         height = element["height"]

    #         # Convert color values (assuming they are normalized between 0-1)
    #         color = (
    #             int(element["color_r"] * 255),
    #             int(element["color_g"] * 255),
    #             int(element["color_b"] * 255)
    #         )

    #         # Adjust negative positions (move elements into the visible screen area)
    #         x = max(0, x)
    #         y = max(0, y)

    #         # Draw the rectangle (UI element)
    #         draw.rectangle([x, y, x + width, y + height], outline="black", fill=color)

    #     # Save and show the generated UI image
    #     image.save(output_image_path)
    #     image.show()

    #     print("Image saved as ui_output.png")



    # Step 1: Save json in extracted features folder
    # egfe_ui_processing.process_ui_elements(json_folder, output_folder)
    
    # Step 2: Split Data into Train and Test
    # splitter.save_split_files(train_folder, test_folder)
    
    # Step 3: Load Normalized train data
    # train_data = egfe_load_data.load_unnormalized_data(train_folder)
    # print(train_data)
    
    # Step 4: Visualize UI Elements (Scatter Plot)
    #egfe_visualization.scatter_plot_ui_elements(train_data)
    
    # Step 5: DBSCAN Clustering Based on selected feature
    clustered_data, clusters = egfe_clustering.dbscan_cluster('color')
    # print (clustered_data)
    # egfe_clustering.handle_outliers(clustered_data, "Color Clustering", "Color Clustering Outliers")
    egfe_clustering_evaluation.evaluate_clustering(clustered_data)


    # print(data)
    # clustered_data_json = output_folder+ '/X-train Clusters based on label and type.json'
    # recognition = RecognitionEvaluation()
    # recognition.evaluate_rule(clustered_data_json,evaluation_folder)

    # testing = RecognitionTesting()
    # testing.evaluate_rule_test(test_folder, evaluation_folder)
    # testing.analyze_test_results(test_folder, train_folder)

    ##############################################################################################################
    
    # Step 6: Visualizing Clustering Results
    # egfe_visualization.clustering_visualization(clustered_data,clusters)
    # egfe_visualization.visualize_alignment_consistency(clustered_data)
    # egfe_visualization.visualize_color_consistency(clustered_data)
    # egfe_visualization.visualize_size_proportionality(clustered_data)
        
    # Step 7: Assign Clusters to Test Data
    # new_x_test = egfe_clustering_testing.assign_test_clusters(clustered_data,test_folder,'label')
    # print(new_x_test)
    # egfe_clustering_testing.save_clusters_to_json(new_x_test , output_folder,'label')
    # print("clustered data:")
    # print(clustered_data)
    # print("new x test data:")
    # print(new_x_test)
    # egfe_clustering_testing.evaluate_test_clusters(new_x_test, clustered_data)
    
    # Step 9: Minimalist Heuristic Evaluation
    # element_count, status = minimalist.count_ui_elements(clustered_data)
    # print("Number of elements =", element_count)
    # print("Status of the elements =", status)

    # rule = Minimalist()
    # feedback = rule.evaluate_rule()

    # minimalist_evaluation.evaluate_rule(train_folder,evaluation_folder)

    # minimalist_test_evaluation.analyze_test_results(train_folder, test_folder)

    # for file_name in os.listdir(test_folder):
    #     file_path = os.path.join(test_folder, file_name)
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             content = f.read().strip()
    #             if not content:
    #                 print(f"Empty file detected: {file_name}")
    #             else:
    #                 print("loaded")
    #                 json.loads(content)  # Try loading JSON to validate
    #     except json.JSONDecodeError:
    #         print(f"Invalid JSON in file: {file_name}")

    # minimalist_evaluation.evaluate_rule(train_folder,evaluation_folder)
#     minimalist_test_evaluation.evaluate_rule_test(test_folder, evaluation_folder)
#     minimalist_evaluation_json = evaluation_folder + '/minimalist_evaluation.json'
#     minimalist_test_evaluation_json = evaluation_folder + '/minimalist_test_evaluation.json'
# #
#     minimalist_test_evaluation.analyze_test_results(minimalist_evaluation_json,minimalist_test_evaluation_json)


    # Recognition
    # recognize = Recognition()
    # # Example dataset
    # data = {
    #     "color": ["#FF0000", "#00FF00", "#0000FF"],
    #     "type": ["button", "input", "label"],  # Only button & input are interactive
    #     "position.x": [50, -20, 300],  # One element is off-screen
    #     "position.y": [100, 200, 400],
    #     "width": [80, 5, 100],  # One element is too small
    #     "height": [40, 20, 50],
    #     "screen_width": [500, 500, 500],
    #     "screen_height": [800, 800, 800],
    # }

    # Convert to DataFrame
    # df = pd.DataFrame(data)

    # # Run visibility check
    # df_result = recognize.minimized_memory_load(df)

    # # Print results
    # print(df_result)


    ##############################################################################################

    # base_path = Path(_file_).resolve().parent  # Get current script directory
    # file_path = base_path / "data/raw/EGFE/extractedFeatures/X-train clusters.json"

    # if not file_path.exists():
    #     raise FileNotFoundError(f"File not found: {file_path}")

    # evaluator = EGFE_HeuristicEvaluation(str(file_path))
    # # evaluation_results = evaluator.evaluate_minimalist_on_clusters()
    # evaluator.evaluate_minimalist()
    # print(evaluator.evaluate_minimalist())

    # Testing
    # minimalist_testing = MinimalistTesting()

    # # Evaluate test data
    # print("\nEvaluating test data...")
    # minimalist_tester.evaluate_rule_test(test_folder, evaluation_folder)

    # # Analyze test results and calculate Precision, Recall, and F1 Score
    # print("\nAnalyzing test results...")
    # minimalist_tester.analyze_test_results(train_json_path, test_json_path)



    # clusters_data_path = "project/data/raw/EGFE/extractedFeatures/X-train clusters.json"
    # base_path = Path(__file__).resolve().parent  # Get current script directory
    # clusters_data_path = base_path / "data/raw/EGFE/extractedFeatures/X-train clusters.json"
# 
    # with open(clusters_data_path, "r") as file:
        # clusters_data = json.load(file)

    # minimalist_checker = Minimalist()
    # feedback = minimalist_checker.evaluate_rule(clusters_data)
    # for f in feedback:
    #     print(f)

    # base_path = Path(__file__).resolve().parent  # Get current script directory
    # clusters_data_path = base_path / "data/raw/EGFE/extractedFeatures/X-train clusters.json"

    # with open(clusters_data_path, "r") as file:
    #     clusters_data = json.load(file)

    # rule = Minimalist()
    # evaluator = MinimalistEvaluation()
    # evaluator.evaluate_minimalist(train_folder, evaluation_folder)



    # # for cluster_id, elements in clusters_data.items():
    # feedback = rule.evaluate_rule(clusters_data)
    # # print(f"\n{cluster_id}:")
    # for message in feedback:
    #     print(f"  - {message}")


    # base_path = Path(__file__).resolve().parent  # Get current script directory
 
    # Load all test JSON files into a dictionary
    # test_clusters = {}  

    # test_json_files = [f for f in os.listdir(test_folder) if f.endswith(".json")]

    # for test_file in test_json_files:
    #     test_json_path = os.path.join(test_folder, test_file)

    #     with open(test_json_path, "r", encoding="utf-8") as f:
    #         data = json.load(f)  # Load JSON file content as dictionary

    #     test_clusters.update(data)  # Merge all test files into one dictionary

    # Run evaluation with correctly loaded test data
    # print("Running Minimalist Rule Evaluation on Test Data...")
    # evaluator.evaluate_minimalist_test(test_data, evaluation_folder)
    # print("Running Minimalist Rule Evaluation on Test Data...")
    # evaluator.evaluate_minimalist_test(test_data, evaluation_folder)

    # # Load training results
    # train_json = os.path.join(evaluation_folder, "minimalist_evaluation.json")

    # Analyze results for each test file separately
    # for test_file in test_json_files:
        # test_json_path = os.path.join(test_folder, test_file)
        # print(f"\nAnalyzing Results for {test_file}...")
        # evaluator.analyze_results(train_json, test_json_path)

    


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




