import json
import json
from components.Clustering_Component.EGFE_clustering import EGFE_Clustering
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory

import pandas as pd

from project.components.Feedback_Generator_Component.heuristics.Consistency_using_clusters import ClusteringConsistency
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

