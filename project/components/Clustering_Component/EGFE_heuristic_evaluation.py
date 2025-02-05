import json
import json
import os
import pandas as pd

from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Feedback_Generator_Component.heuristics.Consistency_using_clusters import ClusteringConsistency


dataset_folder = './data/raw/EGFE'
output_folder = dataset_folder + '/extractedFeatures'
train_folder = output_folder + '/train'

class EGFE_HeuristicEvaluation():    
    def __init__(self):
        self.clustering = EGFE_Clustering(train_folder, output_folder)
        # self.cluster_json_file = cluster_json_file
        # with open(cluster_json_file, 'r') as f:
        #     self.clusters = json.load(f)

    def evaluate_minimalist_on_designs(self, train_folder, output_folder):
        minimalist_instance = HeuristicFactory.check_rule("minimalist")

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(file_name)
                white_space_ratio, feedback = minimalist_instance.evaluate_minimalist(data,data['screen_size']['screen_width'],data['screen_size']['screen_height'])
                # print(feedback)
                # Store elements with their evaluation
                result_data = {
                    "design_id": file_name,
                    "screen_size": data["screen_size"],
                    "white_space_ratio": white_space_ratio,
                    "evaluation": feedback,
                    "elements": data["elements"]  # Keeping all elements in the result file
                }

                # Save result in a new JSON file
                # self.save_white_space_ratio_evaluation_result(file_name, result_data, output_folder)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")

    def save_white_space_ratio_evaluation_result(self, file_name, result_data, output_folder):
        """ Saves the evaluation result for each design in a new JSON file """

        output_path = os.path.join(output_folder, f"evaluated_{file_name}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=4)

        print(f"Evaluation results saved to {output_path}")
    def evaluate_consistency(self):
        # """Evaluate consistency for the clusters loaded from JSON."""
        # Convert clusters JSON into a DataFrame (needed for the consistency checker)
       
        df = pd.DataFrame([elem for cluster in self.clusters for elem in cluster['elements']])
        df['Cluster'] = [cluster['Cluster'] for cluster in self.clusters for _ in cluster['elements']]

        # Pass the dataframe to the consistency checker
        consistency_checker = ClusteringConsistency(df)
        consistency_report = consistency_checker.generate_consistency_report()
        print("\n Consistency Report:")
        print(consistency_report)

        # Identify inconsistent clusters based on spacing
        inconsistent_clusters = consistency_checker.detect_inconsistent_clusters()
        print(f"\n Inconsistent Clusters: {inconsistent_clusters}")

        # Plot alignment consistency
        consistency_checker.plot_alignment_consistency()

