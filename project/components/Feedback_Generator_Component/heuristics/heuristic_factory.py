from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface
from components.Feedback_Generator_Component.heuristics.consistency import Consistency
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist
from components.Feedback_Generator_Component.heuristics.Consistency_using_clusters import ClusteringConsistency


class HeuristicFactory:
   def check_rule(rule_type: str, df=None) -> HeuristicInterface:
        heuristics = {
            "consistency": Consistency,
            "minimalist": Minimalist,
            "ClusteringConsistency": lambda: ClusteringConsistency(df) if df is not None else None  # Pass df safely
        }

        if rule_type in heuristics:
            heuristic_instance = heuristics[rule_type]()
            if heuristic_instance is None:
                raise ValueError(f"Missing required dataset for heuristic: {rule_type}")
            return heuristic_instance 

    