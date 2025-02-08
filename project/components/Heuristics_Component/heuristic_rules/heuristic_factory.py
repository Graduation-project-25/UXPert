from components.Heuristics_Component.heuristic_rules.Consistency_using_clusters import ClusteringConsistency
from components.Heuristics_Component.heuristic_rules.consistency import Consistency
from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface
from components.Heuristics_Component.heuristic_rules.recognition import Recognition


class HeuristicFactory:
   def check_rule(rule_type: str, df=None) -> HeuristicInterface:
        # heuristics = {
        #     "consistency": Consistency,
        #     "minimalist": Minimalist,
        #     "recognition": Recognition,
        #     "ClusteringConsistency": lambda: ClusteringConsistency(df) if df is not None else None  # Pass df safely
        # }

        # if rule_type in heuristics:
        #     heuristic_instance = heuristics[rule_type]()
        #     if heuristic_instance is None:
        #         raise ValueError(f"Missing required dataset for heuristic: {rule_type}")
        #     return heuristic_instance 
        
        match rule_type:
            case "consistency":
                return Consistency()
            case "minimalist":
                return Minimalist()
            case "recognition":
                return Recognition()
            case "ClusteringConsistency":
                return ClusteringConsistency(df)
            case _:
                raise ValueError(f"Missing required dataset for heuristic: {rule_type}")


        

    