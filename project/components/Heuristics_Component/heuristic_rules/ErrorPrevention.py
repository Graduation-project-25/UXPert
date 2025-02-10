import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface
import json
import os
import time
class ErrorPrevention(HeuristicInterface):
    
    # Constants
    CONFIRMATION_KEYWORDS = ["confirm","are you sure", "proceed", "continue", "ok", "yes", "no"]
    DANGEROUS_ACTION_KEYWORDS = ["delete", "remove", "discard", "erase", "reset", "clear", "cancel", "terminate"]
    DATA_FOLDER =  "data/figma_features/extracted"
  
    # Global dictionary to store DataFrames for each page
    all_pages_data = {}
    import os

    def load_all_design_pages(self):
        """Load all JSON files in the folder as a dictionary."""
        all_data = {}
        for file_name in os.listdir(self.DATA_FOLDER):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.DATA_FOLDER, file_name)
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        frame_name = data["screen_size"]["frameName"]
                        all_data[frame_name] = data["elements"]
                except (json.JSONDecodeError, KeyError):
                    print(f"Warning: Skipping corrupted file {file_name}")
        return all_data

    def detect_buttons(self, ui_data):
        """Detect dangerous buttons in the design."""
        buttons = []

        if ui_data.empty:
            return buttons  

        ui_data.columns = ui_data.columns.str.strip()

        for _, row in ui_data.iterrows():
            if row.get('hasClickInteraction'):
                element_text = row.get('textContent', '').lower()
                is_icon = row.get('isIcon', 'FALSE') == 'TRUE'  

                is_dangerous = any(keyword in element_text for keyword in self.DANGEROUS_ACTION_KEYWORDS) or is_icon

                buttons.append({
                    "id": row.get("id"),
                    "name": row.get('name', 'Unnamed'),
                    "text": element_text,
                    "clickDestination": row.get("clickDestination", "").strip(),
                    "is_dangerous": is_dangerous
                })

        return buttons

    def check_confirmation_messages(self, ui_data):
        """Check if a dangerous button's destination has a confirmation message."""
        buttons = self.detect_buttons(ui_data)
        dangerous_buttons = [b for b in buttons if b["is_dangerous"]]
        all_design_pages = self.load_all_design_pages()
        confirmation_issues = []
        confirmed_buttons = 0

        if not dangerous_buttons:
            return confirmation_issues, 100  # No dangerous buttons, so no issues.

        for button in dangerous_buttons:
            destination_id = button["clickDestination"].strip()
            has_confirmation = False

            if destination_id:
                for frame_name, elements in all_design_pages.items():
                    for element in elements:
                        text_content = " ".join(element.get("textContent", "").strip().lower().split())

                        # Check if this is the correct destination frame or if it's a text element in the frame
                        if element.get("id") == destination_id or element.get("type") == "TEXT":
                            if any(keyword in text_content for keyword in self.CONFIRMATION_KEYWORDS):
                                has_confirmation = True
                                confirmed_buttons += 1
                                break
                    if has_confirmation:
                        break

            confirmation_issues.append({
                "button_name": button["name"],
                "confirmation_status": "Found confirmation" if has_confirmation else "Missing confirmation"
            })

        confirmation_percentage = (confirmed_buttons / len(dangerous_buttons)) * 100 if dangerous_buttons else 100
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
        """Evaluate error prevention heuristic."""
        ui_data.columns = ui_data.columns.str.strip()
        validation_issues = self.check_input_validation(ui_data)
        confirmation_issues, confirmation_percentage = self.check_confirmation_messages(ui_data)

        total_issues = len(validation_issues) + len(confirmation_issues)
        prevention_score = max(0, 100 - (total_issues * 10))

        if confirmation_percentage < 50:
            prevention_score -= 20  
        feedback = {
            "ErrorPreventionScore": round(max(prevention_score, 0), 2),
            "ValidationIssues": validation_issues,
            "ConfirmationIssues": confirmation_issues,
            "Feedback": {
                "Prevention": "Good error prevention." if prevention_score > 80 else "Needs improvement.",
                "Validation": "Validation issues detected." if validation_issues else "No validation issues.",
                "Confirmation": "Confirmation issues detected." if confirmation_issues else "No confirmation issues."
            }
        }
        return feedback