import pandas as pd

from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorPrevention(HeuristicInterface):
    
    def detect_button_or_input(self, ui_data):
        """Detects buttons or input fields based on attributes such as name, borders, size, and shadow."""
        buttons_and_inputs = []
        
        for _, row in ui_data.iterrows():
            # Detect if it's a button: Check for rounded corners, shadows, and names
            is_button = False
            if row['width'] > 100 and row['height'] > 30:  # Size threshold for buttons
                if row['position.x'] is not None and row['position.y'] is not None:  # Ensure position exists
                    if 'button' in row['name'].lower() or 'submit' in row['name'].lower():  # Check for button-like names
                        is_button = True
                    if row['rotation'] is not None and row['rotation'] > 0:  # Check for possible rotation
                        is_button = True
                    # Check for rounded corners (border radius)
                    if row['width'] > 50 and row['height'] > 50 and (row['color_r'] + row['color_g'] + row['color_b']) < 0.8:
                        is_button = True
                    # Check for shadows (simple heuristic based on color)
                    if row['color_r'] < 0.3 and row['color_g'] < 0.3 and row['color_b'] < 0.3:
                        is_button = True

            # Add button or input field to the list
            if is_button:
                buttons_and_inputs.append(row['name'])

        return buttons_and_inputs

    def check_input_validation(self, ui_data):
        """Checks if input fields have validation messages or required indicators."""
        input_fields = self.detect_button_or_input(ui_data)  # Detect buttons and inputs based on attributes
        validation_errors = []
        
        for field in input_fields:
            # Check for validation indicators like error messages or required indicators
            # Look for nearby 'TEXT' elements (e.g., error messages) near the input fields
            nearby_validations = ui_data[
                (ui_data['type'] == 'TEXT') &  # Ensure we're checking for TEXT type
                (abs(ui_data['position.y'] - ui_data.row['position.y']) < 20)  # Close proximity to input field
            ]
            
            if nearby_validations.empty:
                validation_errors.append(f"Missing validation for input at {field}")
        
        return validation_errors

    def check_confirmation_for_dangerous_actions(self, ui_data):
        """Detects buttons for critical actions and checks if confirmation exists."""
        dangerous_buttons = self.detect_button_or_input(ui_data)  # Detect buttons
        confirmation_warnings = []
        
        for button in dangerous_buttons:
            # Look for confirmation messages nearby (e.g., 'Are you sure?')
            nearby_confirmations = ui_data[
                (ui_data['type'] == 'TEXT') &  # Ensure the confirmation is a TEXT element
                (abs(ui_data['position.y'] - ui_data.row['position.y']) < 50)  # Close proximity to the button
            ]
            
            if nearby_confirmations.empty:
                confirmation_warnings.append(f"No confirmation for dangerous button {button}")
        
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
