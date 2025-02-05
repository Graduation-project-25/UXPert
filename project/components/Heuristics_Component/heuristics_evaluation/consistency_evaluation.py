import pandas as pd
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.Consistency_using_clusters import ClusteringConsistency

class ConsistencyEvaluation(HeuristicEvaluationInterface):    
    # def __init__(self):

    def evaluate_rule(self, designs):
        self.evaluate_consistency(self)


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

