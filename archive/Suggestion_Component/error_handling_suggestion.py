from components.Heuristics_Component.heuristic_rules.ErrorHandling import ErrorHandling
from components.Suggestion_Component.suggestion import SuggestionInterface

class ErrorHandlingSuggestions(SuggestionInterface):
    def __init__(self, error_handling=None):
        self.error_handling = error_handling if error_handling else ErrorHandling()

    def suggest_error_fixes(self, ui_data):
        """Provide suggestions to improve error messages and recovery options."""
        suggestions = []

        # Get detected issues
        error_issues, error_suggestions = self.error_handling.check_error_messages(ui_data)
        recovery_issues, recovery_suggestions = self.error_handling.check_recovery_options(ui_data)

        # Suggest fixes for unclear error messages
        for issue in error_issues:
            if "empty" in issue:
                suggestions.append({
                    "text": "Ensure all error messages contain meaningful text.",
                    "action": {
                        "type": "update_text",
                        "fix": "Provide clear and informative error messages."
                    }
                })
            elif "too short" in issue:
                suggestions.append({
                    "text": "Make error messages at least 3 words long for clarity.",
                    "action": {
                        "type": "expand_text",
                        "min_length": 3
                    }
                })
            elif "visually distinguishable" in issue:
                suggestions.append({
                    "text": "Use red color, bold text, or an alert icon to highlight error messages.",
                    "action": {
                        "type": "style_update",
                        "properties": {"color": "red", "fontWeight": "bold"}
                    }
                })

        # Suggest fixes for missing recovery options
        for issue in recovery_issues:
            if "No visible recovery options" in issue:
                suggestions.append({
                    "text": "Consider adding recovery options such as 'Retry', 'Help', or 'Undo' buttons.",
                    "action": {
                        "type": "add_buttons",
                        "buttons": ["Retry", "Help", "Undo"]
                    }
                })

        return suggestions
