import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ErrorPrevention(HeuristicInterface):

    CONFIRMATION_KEYWORDS = ["confirm", "are you sure", "proceed", "continue", "ok", "yes", "no"]

    def detect_buttons(self, ui_data):
        """Detects buttons based on click interactions."""
        buttons = []

        if ui_data.empty:
            return buttons  

        for _, row in ui_data.iterrows():
            if row.get('hasClickInteraction') or row.get('hasHoverInteraction'):
                buttons.append({"name": row.get('name', 'Unnamed'), "position.y": row.get("position.y")})
        
        return buttons

    def check_confirmation_messages(self, ui_data):
        """Checks if confirmation messages are present near buttons."""
        buttons = self.detect_buttons(ui_data)
        confirmation_issues = []
        total_buttons = len(buttons)
        confirmed_buttons = 0

        for button in buttons:
            button_name = button["name"]
            button_y = button["position.y"]
            has_confirmation = False

            for _, row in ui_data.iterrows():
                if row['type'] == 'TEXT' and abs(row['position.y'] - button_y) < 50:
                    text_content = row.get("name", "").lower()
                    if any(keyword in text_content for keyword in self.CONFIRMATION_KEYWORDS):
                        has_confirmation = True
                        confirmed_buttons += 1
                        break

            if not has_confirmation:
                confirmation_issues.append(f"No confirmation for button: {button_name}")

        # Calculate confirmation percentage
        confirmation_percentage = (confirmed_buttons / total_buttons * 100) if total_buttons > 0 else 100

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
        if confirmation_percentage < 20:
            prevention_score -= 20  # Penalize if confirmation messages are below 50%

        feedback = {
            "ErrorPreventionScore": max(prevention_score, 0),
            "ValidationIssues": validation_issues,
            "ConfirmationIssues": confirmation_issues,
            "Feedback": "Good error prevention" if prevention_score > 80 else "Needs improvement."
        }

        return feedback
