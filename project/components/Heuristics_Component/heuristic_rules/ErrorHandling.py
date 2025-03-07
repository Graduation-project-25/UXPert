import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorHandling(HeuristicInterface):

    def check_error_messages(self, ui_data):
        """Check for clear, informative, and distinguishable error messages in the design."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        error_keywords = ['error', 'warning', 'fail', 'invalid', 'oops', 'unexpected', 'denied']
        issues = []

        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() == 'TEXT' and any(keyword in row.get('name', '').lower() for keyword in error_keywords):
                text_content = row.get('textContent', '').strip()
                
                if not text_content:
                    issues.append(f"Error message '{row['name']}' is present but empty.")
                
                elif len(text_content.split()) < 3:
                    issues.append(f"Error message '{row['name']}' is too short and unclear.")
                
                if not any(keyword in row.get('style', '').lower() for keyword in ['red', 'bold', 'alert', 'warning']):
                    issues.append(f"Error message '{row['name']}' may not be visually distinguishable.")

        return issues

    def check_recovery_options(self, ui_data):
        """Check if there are sufficient recovery options available for users when an error occurs."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        recovery_keywords = ['retry', 'fix', 'help', 'undo', 'cancel', 'support', 'contact', 'report', 'reset']
        issues = []
        recovery_elements = 0

        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() in ['BUTTON', 'LINK'] and any(keyword in row.get('name', '').lower() for keyword in recovery_keywords):
                recovery_elements += 1

        if recovery_elements == 0:
            issues.append("No visible recovery options found (e.g., retry, help, or undo buttons).")

        return issues

    def evaluate_rule(self, ui_data):
        """Evaluate error handling heuristic with severity-based scoring."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        required_columns = {'type', 'name', 'textContent', 'style'}
        missing_columns = required_columns - set(ui_data.columns)
        if missing_columns:
            return {"error": f"Missing required columns: {missing_columns}"}


        error_issues = self.check_error_messages(ui_data)
        recovery_issues = self.check_recovery_options(ui_data)


        error_penalty = sum(15 if "empty" in issue else 10 for issue in error_issues)
        recovery_penalty = sum(10 for _ in recovery_issues)
        total_penalty = min(error_penalty + recovery_penalty, 100) 

        error_handling_score = max(0, 100 - total_penalty)

        feedback = {
            "ErrorHandlingScore": round(error_handling_score, 2),
            "ErrorIssues": error_issues,
            "RecoveryIssues": recovery_issues,
            "Feedback": {
                "Errors": "Error messages are clear and well-formed." if not error_issues else "Some error messages need improvement.",
                "Recovery": "Recovery options are available." if not recovery_issues else "Consider adding help/recovery buttons."
            },
            "Suggestions": {
                "Error Messages": "Ensure error messages are descriptive, distinguishable (color, bold), and provide actionable solutions.",
                "Recovery": "Provide 'Retry', 'Help', or 'Undo' options near errors to improve usability."
            }
        }

        return feedback
