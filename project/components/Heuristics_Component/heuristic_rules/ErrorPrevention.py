import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface
import json
import os
import time
class ErrorPrevention(HeuristicInterface):
    
    # Constants
    CONFIRMATION_KEYWORDS = ["confirm","are you sure", "proceed", "continue", "ok", "yes", "no"]
    DANGEROUS_ACTION_KEYWORDS = ["delete", "remove", "discard", "erase", "reset", "clear", "cancel", "terminate"]

    # Global dictionary to store DataFrames for each page
    all_pages_data = {}
    import os

    def debug_json():
        """Check if the JSON file exists and print its contents."""
        if os.path.exists('all_pages_data.json'):
            with open('all_pages_data.json', 'r') as f:
                print("Debug: Current JSON File Contents")
                print(f.read())  # Print the raw JSON content
        else:
            print("Debug: JSON file does not exist yet.")

    def store_page_data(self, page_name, ui_data):
        """Store DataFrame for each page in a JSON file and ensure it's fully written."""
        page_data = ui_data.to_dict(orient='records')

        try:
            with open('all_pages_data.json', 'r') as f:
                all_data = json.load(f)
        except FileNotFoundError:
            all_data = {}

        all_data[page_name] = page_data

        # Open in write mode to ensure full write
        with open('all_pages_data.json', 'w') as f:
            json.dump(all_data, f, indent=4)
            f.flush()  # Ensure write is completed
            os.fsync(f.fileno())  # Flush file to disk while it's still open

        # Small delay to ensure OS registers file update
        time.sleep(0.5)


    def detect_buttons(self, ui_data):
        """Detects buttons and identifies if they perform dangerous actions. Also distinguishes dangerous icons."""
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
                    "name": row.get('name', 'Unnamed'),
                    "text": element_text,
                    "position.y": row.get("position.y"),
                    "is_dangerous": is_dangerous,
                    "is_icon": is_icon  
                })

        return buttons

    def check_confirmation_messages(self, ui_data, page_name):
        """Checks if confirmation messages are present near dangerous buttons."""
        buttons = self.detect_buttons(ui_data)
        confirmation_issues = []
        dangerous_buttons = [b for b in buttons if b["is_dangerous"]]
        confirmed_buttons = 0
        total_dangerous_buttons = len(dangerous_buttons)

        if total_dangerous_buttons == 0:
            return confirmation_issues, 100  

        try:
            with open('all_pages_data.json', 'r') as f:
                all_data = json.load(f)
        except FileNotFoundError:
            return confirmation_issues, 0  

        for button in dangerous_buttons:
            button_name = button["name"]
            has_confirmation = False

            click_destination = ui_data.loc[ui_data['name'] == button_name, 'clickDestination'].values if 'clickDestination' in ui_data.columns else None

            if click_destination and click_destination[0]:  
                destination_id = click_destination[0].strip()  
                destination_id = destination_id.replace('I3:', '').strip()  

                # Debugging info
                print(f"Debug: Checking destination ID: {destination_id}")

                # Iterate over frames in the JSON file to find destination ID
                for page, frames in all_data.items():
                    for frame in frames:
                        if frame.get("id") == destination_id:
                            print(f"Debug: Found frame with ID {destination_id} in {page}")

                            text_content = frame.get("textContent", "").lower()
                            if any(keyword in text_content for keyword in self.CONFIRMATION_KEYWORDS):
                                has_confirmation = True
                                confirmed_buttons += 1
                                break
                    if has_confirmation:
                        break  

            if has_confirmation:
                confirmation_issues.append({
                    "button_name": button_name,
                    "confirmation_status": "Found confirmation"
                })
            else:
                confirmation_issues.append({
                    "button_name": button_name,
                    "confirmation_status": "Missing confirmation"
                })

        return confirmation_issues, confirmed_buttons / total_dangerous_buttons * 100

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

   

    def wait_for_json_update(expected_page, expected_data, timeout=2.0, interval=0.5):
        """Wait until the JSON file contains the expected page data."""
        start_time = time.time()
        
        # Ensure expected_data is a list
        if not isinstance(expected_data, list):
            print("Error: expected_data is not a list. It should be a list of dictionaries.")
            return False

        while time.time() - start_time < timeout:
            try:
                with open('all_pages_data.json', 'r') as f:
                    all_data = json.load(f)
                    # Ensure we are comparing lists of records
                    if expected_page in all_data:
                        # Compare lists of dictionaries (order should also match)
                        if all_data[expected_page] == expected_data:
                            return True  # JSON has updated
            except (FileNotFoundError, json.JSONDecodeError):
                pass  # Ignore errors and retry

            time.sleep(interval)  # Wait before retrying

        print(f"Warning: JSON update for {expected_page} not detected within {timeout} seconds.")
        return False  # Timeout occurred


    def evaluate_rule(self, ui_data, page_name):
        """Ensures all frames are stored before evaluating error prevention rules."""
        ui_data.columns = ui_data.columns.str.strip()

        # Step 1: Store the UI data for the current page
        self.store_page_data(page_name, ui_data)

        # Log the expected data
        expected_data = ui_data.to_dict(orient='records')
        # print(f"Debug: Expected data for page {page_name}: {expected_data}")

        # Step 2: Wait for the JSON file to be fully updated before continuing
        if not self.wait_for_json_update(page_name, expected_data):
            print("Error: JSON file did not update in time, proceeding with old data.")

        # Step 3: Load all stored UI data after ensuring it's updated
        for _ in range(3):  # Retry multiple times if needed
            try:
                with open('all_pages_data.json', 'r') as f:
                    all_data = json.load(f)
                break  # Exit loop if reading is successful
            except (FileNotFoundError, json.JSONDecodeError):
                time.sleep(0.5)  # Wait and retry

        # Step 4: Perform heuristic evaluations now that all frames are available
        validation_issues = self.check_input_validation(ui_data)
        confirmation_issues, confirmation_percentage = self.check_confirmation_messages(ui_data, page_name)

        total_issues = len(validation_issues) + len(confirmation_issues)
        prevention_score = max(0, 100 - (total_issues * 10))

        if confirmation_percentage < 50:
            prevention_score -= 20  

        feedback = {
            "ErrorPreventionScore": max(prevention_score, 0),
            "ValidationIssues": validation_issues,
            "ConfirmationIssues": confirmation_issues,
            "Feedback": "Good error prevention" if prevention_score > 80 else "Needs improvement."
        }

        return feedback