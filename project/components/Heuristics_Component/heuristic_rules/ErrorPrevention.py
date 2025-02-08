import pandas as pd

class ErrorPrevention:
    def __init__(self, ui_data):
        """
        ui_data: DataFrame containing UI elements with columns:
        ['element_type', 'text', 'position_x', 'position_y', 'width', 'height', 'color_r', 'color_g', 'color_b']
        """
        self.ui_data = ui_data

    def check_input_validation(self):
        """Checks if input fields have validation messages or required indicators."""
        input_fields = self.ui_data[self.ui_data['element_type'] == 'input']
        validation_errors = []

        for _, row in input_fields.iterrows():
            # Check if there's a nearby validation message
            nearby_validations = self.ui_data[
                (self.ui_data['element_type'] == 'text') & 
                (abs(self.ui_data['position_y'] - row['position_y']) < 20)  # Close to input field
            ]
            if nearby_validations.empty:
                validation_errors.append(f"Missing validation for input at ({row['position_x']}, {row['position_y']})")

        return validation_errors

    def check_confirmation_for_dangerous_actions(self):
        """Detects buttons for critical actions and checks if confirmation exists."""
        dangerous_buttons = self.ui_data[
            (self.ui_data['element_type'] == 'button') & 
            (self.ui_data['text'].str.lower().isin(['delete', 'reset', 'remove']))
        ]
        confirmation_warnings = []

        for _, row in dangerous_buttons.iterrows():
            # Check if there's a confirmation message nearby
            nearby_confirmations = self.ui_data[
                (self.ui_data['element_type'] == 'dialog') & 
                (abs(self.ui_data['position_y'] - row['position_y']) < 50)
            ]
            if nearby_confirmations.empty:
                confirmation_warnings.append(f"No confirmation for {row['text']} button at ({row['position_x']}, {row['position_y']})")

        return confirmation_warnings

    def generate_error_prevention_report(self):
        """Generates a summary report of error prevention issues."""
        validation_issues = self.check_input_validation()
        confirmation_issues = self.check_confirmation_for_dangerous_actions()

        total_issues = len(validation_issues) + len(confirmation_issues)
        prevention_score = max(0, 100 - (total_issues * 10))  # Reduce score for each issue

        return {
            "ErrorPreventionScore": prevention_score,
            "ValidationIssues": validation_issues,
            "ConfirmationIssues": confirmation_issues,
            "Feedback": "Good error prevention" if prevention_score > 80 else "Needs improvement."
        }
