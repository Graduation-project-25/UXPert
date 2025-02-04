import json
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist


class EGFE_HeuristicEvaluation():    
    def __init__(self, cluster_json_file):
        self.cluster_json_file = cluster_json_file
        with open(cluster_json_file, 'r') as f:
            self.clusters = json.load(f)


    def evaluate_heuristics(self):
        minimalist_instance = HeuristicFactory.check_rule("minimalist")
        minimalist = Minimalist()
        for cluster in self.clusters:
            print(cluster)
            for design_json in cluster['elements']:  
                screen_width = design_json["screen_width"]
                screen_height = design_json["screen_height"]
                result = minimalist.evaluate_minimalist(design_json, screen_width, screen_height)
                print(result)
                # design_json["aesthetic_evaluation"] = result  # Add evaluation to the design
                
        # Optionally, save the updated clusters back to a new file
        # with open('evaluated_clusters.json', 'w') as f:
        #     json.dump(self.clusters, f, indent=4)

    def evaluate_minimalist_on_clusters(self):
        DBSCAN_dataset, clusters = self.dbscan_cluster_based_on_screen_size_and_type()

        # Initialize Minimalist rule
        minimalist_rule = Minimalist()  
        cluster_feedback = {}

        for cluster in clusters:
            # Ignore noise points
            if cluster == -1:
                continue  

            # Filter cluster data
            cluster_data = DBSCAN_dataset[DBSCAN_dataset["Cluster"] == cluster]  
            
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

