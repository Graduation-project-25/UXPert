import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorHandling(HeuristicInterface):

    def check_error_messages(self, ui_data):
        """Check for clear and informative error messages in the design."""
        ui_data = ui_data.fillna('')  # Replace missing values with empty strings
        ui_data.columns = ui_data.columns.str.strip()
        
        issues = []
        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() == 'TEXT' and 'error' in row.get('name', '').lower():
                text_content = row.get('textContent', '').strip()
                if not text_content:
                    issues.append(f"Error message '{row['name']}' is present but empty.")
                elif len(text_content.split()) < 3:
                    issues.append(f"Error message '{row['name']}' is too short and unclear.")

        return issues

    def check_recovery_options(self, ui_data):
        """Check if there are recovery options available for users when an error occurs."""
        ui_data = ui_data.fillna('')  # Handle missing values
        ui_data.columns = ui_data.columns.str.strip()
        
        issues = []
        recovery_buttons = sum(
            1 for _, row in ui_data.iterrows()
            if row.get('type', '').strip().upper() == 'BUTTON' and any(keyword in row.get('name', '').lower() for keyword in ["retry", "fix", "help"])
        )

        if recovery_buttons == 0:
            issues.append("No help buttons or recovery options available when an error occurs.")

        return issues

    def evaluate_rule(self, ui_data):
        """Evaluate this heuristic by checking error messages and recovery options."""
        ui_data = ui_data.fillna('')  # Prevent missing value errors
        ui_data.columns = ui_data.columns.str.strip()
        
        # Ensure all required columns exist
        required_columns = {'type', 'name', 'textContent'}
        missing_columns = required_columns - set(ui_data.columns)
        if missing_columns:
            return {"error": f"Missing required columns: {missing_columns}"}

        # Run evaluations
        error_issues = self.check_error_messages(ui_data)
        recovery_issues = self.check_recovery_options(ui_data)

        # Calculate error handling score
        total_issues = len(error_issues) + len(recovery_issues)
        error_handling_score = max(0, 100 - (total_issues * 10))

        # Return structured feedback
        feedback = {
            "ErrorHandlingScore": round(error_handling_score, 2),
            "ErrorIssues": error_issues,
            "RecoveryIssues": recovery_issues,
            "Feedback": {
                "Errors": "Error messages are clear and informative." if not error_issues else "Error messages need improvement.",
                "Recovery": "There are recovery options available." if not recovery_issues else "Add help buttons or recovery instructions."
            }
        }
        return feedback
