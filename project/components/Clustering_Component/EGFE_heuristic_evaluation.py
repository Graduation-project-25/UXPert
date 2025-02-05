import json
import os
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering

dataset_folder = './data/raw/EGFE'
output_folder = dataset_folder + '/extractedFeatures'
train_folder = output_folder + '/train'

class EGFE_HeuristicEvaluation():    
    def __init__(self):
        self.clustering = EGFE_Clustering(train_folder, output_folder)
        # self.cluster_json_file = cluster_json_file
        # with open(cluster_json_file, 'r') as f:
        #     self.clusters = json.load(f)


    def evaluate_minimalist_on_designs(self, train_folder):
        minimalist = Minimalist()
        minimalist_instance = HeuristicFactory.check_rule("minimalist")

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(file_name)
                result = minimalist.evaluate_minimalist(data,data['screen_size']['screen_width'],data['screen_size']['screen_width'])
                print(result)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")
        # for element in data['elements']:

        # print(data)


        # print(self.clusters)
        # minimalist = Minimalist()
        # for cluster_id, elements in self.clusters.items():
        #     print(elements)
        #     if not elements:  # If the cluster is empty, assume full white space
        #         evaluation = "Pass - Minimalist Design"
        #     else:
        #         screen_width = elements[0]["screen_width"]
        #         screen_height = elements[0]["screen_height"]
        #         evaluation = minimalist.evaluate_minimalist(elements, screen_width, screen_height)
        #     # Store evaluation in each element
        #     for element in elements:
        #         element["aesthetic_evaluation"] = evaluation
            # Save results to JSON
            # with open('evaluated_clusters.json', 'w') as f:
                # json.dump(self.clusters, f, indent=4)







        # Optionally, save the updated clusters back to a new file
        # with open('evaluated_clusters.json', 'w') as f:
        #     json.dump(self.clusters, f, indent=4)

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

