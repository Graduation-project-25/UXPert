from components.Heuristics_Component.ErrorHandling import ErrorHandling
from components.Heuristics_Component.ErrorPrevention import ErrorPrevention
from components.Heuristics_Component.consistency import Consistency
from components.Heuristics_Component.minimalist import Minimalist
from components.Heuristics_Component.heuristic import HeuristicInterface
from components.Heuristics_Component.recognition import Recognition


class HeuristicFactory:
   def check_rule(rule_type: str) -> HeuristicInterface:
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

        
    