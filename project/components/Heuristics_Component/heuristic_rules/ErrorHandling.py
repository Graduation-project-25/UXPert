import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorHandling(HeuristicInterface):

    def check_error_messages(self, ui_data):
        """Check for clear and informative error messages in the design."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        error_keywords = ['error', 'warning', 'fail', 'invalid']
        issues = []

        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() == 'TEXT' and any(keyword in row.get('name', '').lower() for keyword in error_keywords):
                text_content = row.get('textContent', '').strip()
                if not text_content:
                    issues.append(f"Error message '{row['name']}' is present but empty.")
                elif len(text_content.split()) < 3:
                    issues.append(f"Error message '{row['name']}' is too short and unclear.")

        return issues

    def check_recovery_options(self, ui_data):
        """Check if there are recovery options available for users when an error occurs."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        recovery_keywords = ['retry', 'fix', 'help', 'undo', 'cancel', 'support']
        issues = []
        recovery_buttons = sum(
            1 for _, row in ui_data.iterrows()
            if row.get('type', '').strip().upper() == 'BUTTON' and any(keyword in row.get('name', '').lower() for keyword in recovery_keywords)
        )

        if recovery_buttons == 0:
            issues.append("No help buttons or recovery options available for errors.")

        return issues

    def evaluate_rule(self, ui_data):
        """Evaluate error handling heuristic by checking error messages and recovery options."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        # Validate required columns
        required_columns = {'type', 'name', 'textContent'}
        missing_columns = required_columns - set(ui_data.columns)
        if missing_columns:
            return {"error": f"Missing required columns: {missing_columns}"}

        # Run heuristic checks
        error_issues = self.check_error_messages(ui_data)
        recovery_issues = self.check_recovery_options(ui_data)

        error_penalty = len(error_issues) * 10  
        recovery_penalty = len(recovery_issues) * 5 
        total_penalty = error_penalty + recovery_penalty

        error_handling_score = max(0, 100 - total_penalty)

        # Detailed feedback
        feedback = {
            "ErrorHandlingScore": round(error_handling_score, 2),
            "ErrorIssues": error_issues,
            "RecoveryIssues": recovery_issues,
            "Feedback": {
                "Errors": " Error messages are clear and informative." if not error_issues else " Error messages need improvement.",
                "Recovery": " Recovery options are available." if not recovery_issues else " Consider adding help/recovery buttons."
            }
        }
        return feedback
