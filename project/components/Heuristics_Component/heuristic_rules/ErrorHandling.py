import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorHandling(HeuristicInterface):

    def preprocess_data(self, ui_data):
        """Ensure required columns exist and clean the data."""
        ui_data = ui_data.fillna('')
        ui_data.columns = ui_data.columns.str.strip()

        # Define required columns and fill missing ones with default values
        required_columns = {'id', 'type', 'name', 'textContent', 'style', 'parent_id'}
        missing_columns = required_columns - set(ui_data.columns)

        for column in missing_columns:
            ui_data[column] = ''  

        return ui_data

    def check_error_messages(self, ui_data):
        """Check for clear, informative, and distinguishable error messages in the design."""
        ui_data = self.preprocess_data(ui_data)

        error_keywords = ['error', 'warning', 'fail', 'invalid', 'oops', 'unexpected', 'denied']
        guidance_keywords = ['correct', 'fix', 'provide', 'enter', 'check', 'format']
        issues = []
        styles_used = set()

        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() == 'TEXT' and any(keyword in row.get('name', '').lower() for keyword in error_keywords):
                text_content = row.get('textContent', '').strip()
                style = row.get('style', '').lower()
                styles_used.add(style)
                
                if not text_content:
                    issues.append(f"Error message '{row['name']}' is present but empty.")
                elif len(text_content.split()) < 3:
                    issues.append(f"Error message '{row['name']}' is too short and unclear.")
                
                if not any(kw in style for kw in ['red', 'bold', 'alert', 'warning']):
                    issues.append(f"Error message '{row['name']}' may not be visually distinguishable.")

                if not any(kw in text_content.lower() for kw in guidance_keywords):
                    issues.append(f"Error message '{row['name']}' lacks guidance on how to fix the issue.")

        if len(styles_used) > 1:
            issues.append("Inconsistent styles found for error messages.")

        return issues

    def check_recovery_options(self, ui_data):
        """Check if there are sufficient recovery options available for users when an error occurs."""
        ui_data = self.preprocess_data(ui_data)

        recovery_keywords = ['retry', 'fix', 'help', 'undo', 'cancel', 'support', 'contact', 'report', 'reset']
        vague_button_names = ['ok', 'submit', 'continue']
        issues = []
        recovery_elements = 0

        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() in ['BUTTON', 'LINK']:
                name = row.get('name', '').lower()
                if any(keyword in name for keyword in recovery_keywords):
                    recovery_elements += 1
                elif name in vague_button_names:
                    issues.append(f"Button '{row['name']}' may not be clear. Consider using a more descriptive label.")

        if recovery_elements == 0:
            issues.append("No visible recovery options found (retry, help, or undo buttons).")

        return issues

    def check_error_placement(self, ui_data):
        """Ensure error messages are near the relevant UI elements."""
        ui_data = self.preprocess_data(ui_data)

        input_fields = {row['id']: row for _, row in ui_data.iterrows() if row.get('type', '').upper() in ['INPUT', 'TEXT_FIELD']}
        issues = []

        for _, row in ui_data.iterrows():
            if row.get('type', '').strip().upper() == 'TEXT' and 'error' in row.get('name', '').lower():
                related_id = row.get('parent_id', '').strip()
                if related_id and related_id not in input_fields:
                    issues.append(f"Error message '{row['name']}' may not be properly linked to an input field.")

        return issues

    def evaluate_rule(self, ui_data):
        """Evaluate error handling heuristic with severity-based scoring."""
        ui_data = self.preprocess_data(ui_data)

        error_issues = self.check_error_messages(ui_data)
        recovery_issues = self.check_recovery_options(ui_data)
        placement_issues = self.check_error_placement(ui_data)

        error_penalty = sum(15 if "empty" in issue else 10 for issue in error_issues)
        recovery_penalty = sum(10 for _ in recovery_issues)
        placement_penalty = sum(5 for _ in placement_issues)
        total_penalty = min(error_penalty + recovery_penalty + placement_penalty, 100) 

        error_handling_score = max(0, 100 - total_penalty)

        feedback = {
    "ErrorHandlingScore": round(error_handling_score, 2),
    "ErrorIssues": error_issues,
    "RecoveryIssues": recovery_issues,
    "Feedback": f"Errors: {' '.join(error_issues) if error_issues else 'No issues found.'} | "
                f"Recovery: {' '.join(recovery_issues) if recovery_issues else 'Recovery options are available.'}",
    }


        return feedback
