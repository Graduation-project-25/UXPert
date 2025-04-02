from components.Heuristics_Component.heuristic_rules.ErrorHandling import ErrorHandling
from components.Heuristics_Component.heuristic_rules.ErrorPrevention import ErrorPrevention
from components.Heuristics_Component.heuristic_rules.consistency import Consistency
from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface
from components.Heuristics_Component.heuristic_rules.recognition import Recognition


class HeuristicFactory:
   def check_rule(rule_type: str, df=None) -> HeuristicInterface:
        match rule_type:
            case "consistency":
                return Consistency()
            case "minimalist":
                return Minimalist()
            case "recognition":
                return Recognition()
            case "errorPrevention":
                return ErrorPrevention()
            case "errorHandling":
                return ErrorHandling()
            case _:
                raise ValueError(f"Missing required dataset for heuristic: {rule_type}")

        
        

    