from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface
from components.Feedback_Generator_Component.heuristics.consistency import Consistency
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist


class HeuristicFactory:
    def check_rule(rule_type: str) -> HeuristicInterface:
        heuristics = {
            "consistency": Consistency,
            "minimalist": Minimalist,
        }

        if rule_type in heuristics:
            return heuristics[rule_type]()  

    