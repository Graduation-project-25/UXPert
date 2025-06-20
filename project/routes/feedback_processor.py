import hashlib
import json
from typing import Dict, List, Tuple

import concurrent

import pandas as pd
from components.Heuristics_Component.heuristic_factory import HeuristicFactory


class FeedbackProcessor:
    HEURISTIC_RULES = ["consistency", "minimalist", "errorHandling", "errorPrevention", "recognition"]

    def __init__(self):
        self.evaluators = {rule: HeuristicFactory.check_rule(rule) for rule in self.HEURISTIC_RULES}

    def generate_content_hash(self, elements: List[Dict]) -> str:
        """Generate a stable hash of design elements"""
        elements_str = json.dumps(elements, sort_keys=True)
        return hashlib.md5(elements_str.encode()).hexdigest()

    def evaluate_heuristics_parallel(self, elements_df: pd.DataFrame, elements: List[Dict], 
                                   screen_width: int, screen_height: int) -> Tuple[Dict, Dict, Dict, Dict]:
        """Evaluate heuristics in parallel using ThreadPoolExecutor"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                "consistency": executor.submit(self.evaluators["consistency"].evaluate_rule, elements_df),
                "minimalist": executor.submit(self.evaluators["minimalist"].evaluate_rule, 
                                            {"elements": elements}, screen_width, screen_height),
                "errorHandling": executor.submit(self.evaluators["errorHandling"].evaluate_rule, elements_df),
                "errorPrevention": executor.submit(self.evaluators["errorPrevention"].evaluate_rule, elements_df)
            }
            results = {key: future.result() for key, future in futures.items()}
            minimalist_results, _ = results["minimalist"]
            return (results["consistency"], minimalist_results, results["errorHandling"], results["errorPrevention"])

    def process_recognition_feedback(self, elements: List[Dict], screen_width: int, 
                                   screen_height: int) -> List[Dict]:
        """Process recognition feedback for each element"""
        recognition_feedback = []
        for element in elements:
            results = self.evaluators["recognition"].evaluate_rule(
                element, element["type"], screen_width, screen_height,
                element.get("isIconLabeled", False), element["width"], element["height"]
            )
            if results:
                recognition_feedback.append({
                    "element_id": element["id"],
                    "element_name": element.get("name", "Unnamed"),
                    "element_type": element["type"],
                    "Feedback": results
                })
        return recognition_feedback
