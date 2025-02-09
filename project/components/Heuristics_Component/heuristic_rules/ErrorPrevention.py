import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorPrevention(HeuristicInterface):

    CONFIRMATION_KEYWORDS = ["confirm", "are you sure", "proceed", "continue", "ok", "yes", "no"]
    DANGEROUS_ACTION_KEYWORDS = ["delete", "remove", "discard", "erase", "reset", "clear", "cancel", "terminate"]

    def detect_buttons(self, ui_data):
        """Detects buttons and identifies if they perform dangerous actions."""
        buttons = []

        if ui_data.empty:
            return buttons  

        for _, row in ui_data.iterrows():
            if row.get('hasClickInteraction') or row.get('hasHoverInteraction'):
                button_name = row.get('name', '').lower()
                is_dangerous = any(keyword in button_name for keyword in self.DANGEROUS_ACTION_KEYWORDS)

                buttons.append({
                    "name": row.get('name', 'Unnamed'),
                    "position.y": row.get("position.y"),
                    "is_dangerous": is_dangerous
                })
        
        return buttons

    def check_confirmation_messages(self, ui_data):
        """Checks if confirmation messages are present near dangerous buttons."""
        buttons = self.detect_buttons(ui_data)
        confirmation_issues = []
        dangerous_buttons = [b for b in buttons if b["is_dangerous"]]
        confirmed_buttons = 0
        total_dangerous_buttons = len(dangerous_buttons)

        if total_dangerous_buttons == 0:
            return confirmation_issues, 100  # No dangerous buttons → No confirmation needed

        for button in dangerous_buttons:
            button_name = button["name"]
            button_y = button["position.y"]
            has_confirmation = False

            # Check if the button has a click destination
            click_destination = ui_data.loc[ui_data['name'] == button_name, 'clickDestination'].values
            if click_destination and click_destination[0]:  
                destination_id = click_destination[0]
                destination_elements = ui_data[ui_data['id'] == destination_id]  

                # Search for confirmation text in the destination
                for _, row in destination_elements.iterrows():
                    if row['type'] == 'TEXT':
                        text_content = row.get("name", "").lower()
                        if any(keyword in text_content for keyword in self.CONFIRMATION_KEYWORDS):
                            has_confirmation = True
                            confirmed_buttons += 1
                            break
            else:
                # If no clickDestination, check the same page
                for _, row in ui_data.iterrows():
                    if row['type'] == 'TEXT' and abs(row['position.y'] - button_y) < 50:
                        text_content = row.get("name", "").lower()
                        if any(keyword in text_content for keyword in self.CONFIRMATION_KEYWORDS):
                            has_confirmation = True
                            confirmed_buttons += 1
                            break

            if not has_confirmation:
                confirmation_issues.append(f"No confirmation for dangerous button: {button_name}")

        # Calculate confirmation percentage
        confirmation_percentage = (confirmed_buttons / total_dangerous_buttons * 100)

        return confirmation_issues, confirmation_percentage


    def check_input_validation(self, ui_data):
        """Checks if input fields have validation messages or required indicators."""
        input_fields = [row for _, row in ui_data.iterrows() if "input" in row.get('name', '').lower()]
        validation_issues = []

        for field in input_fields:
            field_name = field["name"]
            field_y = field["position.y"]
            has_validation = False

            for _, row in ui_data.iterrows():
                if row['type'] == 'TEXT' and abs(row['position.y'] - field_y) < 20:
                    has_validation = True
                    break

            if not has_validation:
                validation_issues.append(f"Missing validation for input field: {field_name}")

        return validation_issues

    def evaluate_rule(self, ui_data):
        """Generates a summary report of error prevention issues."""
        validation_issues = self.check_input_validation(ui_data)
        confirmation_issues, confirmation_percentage = self.check_confirmation_messages(ui_data)

        # Score calculation
        total_issues = len(validation_issues) + len(confirmation_issues)
        prevention_score = max(0, 100 - (total_issues * 10))

        # Adjust score based on confirmation percentage
        if confirmation_percentage < 50:
            prevention_score -= 20  # Penalize if confirmation messages are below 50% for dangerous actions

        feedback = {
            "ErrorPreventionScore": max(prevention_score, 0),
            "ValidationIssues": validation_issues,
            "ConfirmationIssues": confirmation_issues,
            "Feedback": "Good error prevention" if prevention_score > 80 else "Needs improvement."
        }

        return feedback
