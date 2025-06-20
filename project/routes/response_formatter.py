from typing import Any, Dict, List

from utils.helpers import clean_prefix


class ResponseFormatter:
    """Formats feedback data into API responses"""
    @staticmethod
    def transform_minimalist_results(minimalist_results: Any) -> Dict[str, List[Dict]]:
        """Transform minimalist results into a consistent format"""
        feedback = []
        if isinstance(minimalist_results, dict):
            for key, value in minimalist_results.items():
                issue = ResponseFormatter._map_minimalist_issue(clean_prefix(key))
                feedback.append({
                    "issue": issue,
                    "feedback": clean_prefix(value) if isinstance(value, str) else str(value)
                })
        elif isinstance(minimalist_results, list):
            for item in minimalist_results:
                if isinstance(item, str):
                    issue = ResponseFormatter._map_minimalist_issue(clean_prefix(item))
                    feedback.append({"issue": issue, "feedback": clean_prefix(item)})
                elif isinstance(item, dict):
                    feedback.append({
                        "issue": clean_prefix(item.get('issue', '')),
                        "feedback": clean_prefix(item.get('feedback', '')) if isinstance(item.get('feedback'), str) else str(item.get('feedback', ''))
                    })
        else:
            feedback.append({"issue": "Score", "feedback": clean_prefix(str(minimalist_results))})
        return {"Feedback": feedback}

    @staticmethod
    def _map_minimalist_issue(key: str) -> str:
        """Map cleaned key to standardized issue name"""
        key_lower = key.lower()
        if "white space" in key_lower:
            return "White Space Ratio"
        elif "elements" in key_lower and "irrelevant" not in key_lower:
            return "Number of Elements"
        elif "irrelevant" in key_lower:
            return "Irrelevant Elements"
        elif "score" in key_lower:
            return "Score"
        return key

    @staticmethod
    def prepare_response(error_prevention: Dict, consistency: Dict, error_handling: Dict, 
                        minimalist: Dict, recognition: List[Dict]) -> Dict:
        """Prepare standardized API response"""
        return {
            "message": "Design processed successfully!",
            "status": 200,
            "cached": False,
            "error_prevention_results": {
                "ErrorPreventionScore": f"Error Prevention Score: {error_prevention.get('ErrorPreventionScore', 0)}%.",
                "ValidationIssues": error_prevention.get("ValidationIssues", []),
                "ConfirmationIssues": error_prevention.get("ConfirmationIssues", []),
                "Feedback": error_prevention.get("Feedback", {})
            },
            "consistency_results": {
                "ColorConsistency": f"Color consistency is {consistency.get('ColorConsistency', 0)}%.",
                "AlignmentConsistency": f"Alignment consistency is {consistency.get('AlignmentConsistency', 0)}%.",
                "SizeProportionality": f"Size proportionality is {consistency.get('SizeProportionality', 0)}%.",
                "Feedback": consistency.get('Feedback', {})
            },
            "error_handling_results": {
                "ErrorHandlingScore": f"Error Handling Score: {error_handling.get('ErrorHandlingScore', 0)}%.",
                "RecoveryIssues": error_handling.get("RecoveryIssues", []),
                "Feedback": error_handling
            },
            "minimalist_results": minimalist,
            "recognition_results": recognition
        }

    @staticmethod
    def format_user_history(history: List[Dict]) -> List[Dict]:
        """Format user feedback history"""
        formatted = []
        for item in history:
            formatted.append({
                "design_name": item.get("design_name", "Untitled Design"),
                "frame_name": item.get("frame_name", "Unnamed Frame"),
                "date": item.get("created_at", "").strftime("%Y-%m-%d %H:%M") if item.get("created_at") else "Unknown date",
                "error_prevention_score": next((score for score in [
                    item.get("error_prevention_results", {}).get("ErrorPreventionScore"),
                    item.get("error_prevention_results", {}).get("feedback", {}).get("ErrorPreventionScore")
                ] if score is not None), "N/A"),
                "minimalist_feedback": next((feedback for feedback in [
                    item.get("minimalist_results", {}).get("Feedback"),
                    item.get("minimalist_results", {}).get("feedback", {}).get("Feedback")
                ] if feedback is not None), [])
            })
        return formatted
