import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorPrevention(HeuristicInterface):

     def detect_button_or_input(self, ui_data):
            print(ui_data.head())

            buttons_and_inputs = []

            if ui_data.empty:
                return buttons_and_inputs  

            for _, row in ui_data.iterrows():
                is_button = False
                is_input = False

                # Detect buttons based on interaction triggers
                if row.get('hasClickInteraction') or row.get('hasHoverInteraction'):
                    is_button = True  # Clickable elements are likely buttons

                # Detect input fields
                if not is_button:
                    if row.get('name') and ('input' in row['name'].lower() or 'textfield' in row['name'].lower()):
                        is_input = True

                # Add detected button or input to the list
                if is_button:
                    buttons_and_inputs.append(f"Button: {row.get('name', 'Unnamed')}")
                elif is_input:
                    buttons_and_inputs.append(f"Input: {row.get('name', 'Unnamed')}")

            return buttons_and_inputs


     def check_input_validation(self, ui_data):
        """Checks if input fields have validation messages or required indicators."""
        input_fields = self.detect_button_or_input(ui_data)  # Detect buttons and inputs based on attributes
        validation_errors = []

        for field in input_fields:
            if 'Input' in field:
                # Check for validation indicators like error messages or required indicators
                for _, row in ui_data.iterrows():
                    if row['type'] == 'TEXT' and abs(row['position.y'] - ui_data[ui_data['name'] == field]['position.y'].values[0]) < 20:
                        break
                else:
                    validation_errors.append(f"Missing validation for input at {field}")

        return validation_errors

     def check_confirmation_for_dangerous_actions(self, ui_data):
        """Detects buttons for critical actions and checks if confirmation exists."""
        dangerous_buttons = self.detect_button_or_input(ui_data)  # Detect buttons
        confirmation_warnings = []

        for button in dangerous_buttons:
            if 'Button' in button:
                # Look for confirmation messages nearby (e.g., 'Are you sure?')
                for _, row in ui_data.iterrows():
                    if row['type'] == 'TEXT' and abs(row['position.y'] - ui_data[ui_data['name'] == button]['position.y'].values[0]) < 50:
                        break
                else:
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
