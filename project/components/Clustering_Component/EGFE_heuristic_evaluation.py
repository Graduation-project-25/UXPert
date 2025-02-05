import json
import json
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering

dataset_folder = './data/raw/EGFE'
output_folder = dataset_folder + '/extractedFeatures'
train_folder = output_folder + '/train'
import pandas as pd

from components.Feedback_Generator_Component.heuristics.Consistency_using_clusters import ClusteringConsistency
class EGFE_HeuristicEvaluation():    
    def __init__(self):
        self.clustering = EGFE_Clustering(train_folder, output_folder)
        # self.cluster_json_file = cluster_json_file
        # with open(cluster_json_file, 'r') as f:
        #     self.clusters = json.load(f)

    def evaluate_minimalist_on_designs(self, train_folder, output_folder):
        # minimalist = Minimalist()
        minimalist_instance = HeuristicFactory.check_rule("minimalist")

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(file_name)
                white_space_ratio, feedback = minimalist_instance.evaluate_minimalist(data,data['screen_size']['screen_width'],data['screen_size']['screen_height'])
                print(feedback)
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
    def evaluate_minimalist_on_clusters(self):
        DBSCAN_dataset, clusters = self.clustering.dbscan_cluster('screen_size_and_type')
        
        # Initialize Minimalist rule
        minimalist_rule = Minimalist()  
        cluster_feedback = {}

        for cluster in clusters:
            # Ignore noise points
            if cluster == -1:
                continue  

            # Filter cluster data
            cluster_data = DBSCAN_dataset[DBSCAN_dataset["Cluster"] == cluster]  

            print(cluster_data.columns)
            if 'elements' not in cluster_data.columns:
                raise KeyError("'elements' column is missing from cluster_data.")
            
            # Convert cluster data to a dictionary structure expected by Minimalist
            design_json = {
                "screen_size": {
                    "screen_width": cluster_data["screen_width"].iloc[0],
                    "screen_height": cluster_data["screen_height"].iloc[0]
                },
                "elements": []
            }

            # Extract UI elements from columns that start with "type_"
            for _, row in cluster_data.iterrows():
                for col in cluster_data.columns:
                    if col.startswith("type_") and row[col] > 0:  # Check presence of element
                        design_json["elements"].append({"type": col, "width": 100, "height": 100})

            # Apply Minimalist evaluation
            feedback = minimalist_rule.evaluate_rule(cluster_data)
            cluster_feedback[cluster] = feedback

        return cluster_feedback

    def evaluate_minimalist(self):
        minimalist_rule = Minimalist()
        results = {}

        print(type(self.clusters))
        # print(self.clusters)

        # Check if self.clusters is a dictionary
        if isinstance(self.clusters, dict):
            for cluster_id, cluster_data in self.clusters.items():
                try:
                    feedback = minimalist_rule.evaluate_rule(cluster_data)
                    results[cluster_id] = feedback
                except Exception as e:
                    results[cluster_id] = f"Error evaluating cluster {cluster_id}: {str(e)}"
        else:
            results["error"] = "self.clusters is neither a list nor a dictionary"
        
        return results


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

