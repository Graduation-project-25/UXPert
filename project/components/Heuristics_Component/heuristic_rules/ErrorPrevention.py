import pandas as pd

from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorPrevention(HeuristicInterface):
    # def __init__(self, ui_data):
    #     """
    #     ui_data: DataFrame containing UI elements with columns:
    #     ['type', 'text', 'position_x', 'position_y', 'width', 'height', 'color_r', 'color_g', 'color_b']
    #     """
    #     self.ui_data = ui_data

    def check_input_validation(self, ui_data):
        """Checks if input fields have validation messages or required indicators."""
        # Filter for 'input' fields
        input_fields = ui_data[ui_data['type'] == 'input']
        validation_errors = []

        for _, row in input_fields.iterrows():
            # Look for 'TEXT' elements near the 'input' field (validation messages)
            nearby_validations = ui_data[
                (ui_data['type'] == 'TEXT') &  # Ensure we're checking for TEXT type
                (abs(ui_data['position.y'] - row['position.y']) < 20)  # Close proximity to input field
            ]
            
            if nearby_validations.empty:
                validation_errors.append(f"Missing validation for input at ({row['position.x']}, {row['position.y']})")

        return validation_errors
    

    def check_confirmation_for_dangerous_actions(self, ui_data):
        """Detects buttons for critical actions and checks if confirmation exists."""
        # Filter for buttons with 'delete', 'reset', or 'remove' as part of their text
        dangerous_buttons = ui_data[
            (ui_data['type'] == 'TEXT') &  # Look for button type
            (ui_data['name'].str.lower().isin(['delete', 'reset', 'remove']))  # Look for matching names
        ]
        confirmation_warnings = []

        # for _, row in dangerous_buttons.iterrows():
        #     # Look for 'TEXT' elements (confirmation messages) near the dangerous button
        #     nearby_confirmations = ui_data[
        #         (ui_data['type'] == 'TEXT') &  # Ensure the confirmation is a TEXT element
        #         (abs(ui_data['position.y'] - row['position.y']) < 50)  # Close proximity to the button
        #     ]
            
        if dangerous_buttons.empty:
                confirmation_warnings.append(f"No confirmation messages in the design")

        return confirmation_warnings


    def evaluate_rule(self, ui_data):
        """Generates a summary report of error prevention issues."""
        validation_issues = self.check_input_validation(ui_data)
        confirmation_issues = self.check_confirmation_for_dangerous_actions(ui_data)

        total_issues = len(validation_issues) + len(confirmation_issues)
        prevention_score = max(0, 100 - (total_issues * 10))  # Reduce score for each issue

        feedback = {
            "ErrorPreventionScore": prevention_score,
            "ValidationIssues": validation_issues,
            "ConfirmationIssues": confirmation_issues,
            "Feedback": "Good error prevention" if prevention_score > 80 else "Needs improvement."
        }
        return feedback 