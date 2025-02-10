from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface 


class Recognition(HeuristicInterface):

    def __init__(self):
        pass

    def minimized_memory_load(self, elements_data):
        feedback = []

        # Extract the elements from the JSON structure
        for key, elements in elements_data.items():
            for element in elements:
                if not isinstance(element, dict):  # Skip if it's not a dictionary
                    continue  

                x = element.get("position.x", 0)
                y = element.get("position.y", 0)
                width = element.get("width", 0)
                height = element.get("height", 0)

                # Prevent division by zero
                screen_width = element.get("screen_width", 1920)  
                screen_height = element.get("screen_height", 1080)

                # Determine element type from type_* fields
                element_type = None
                for k, v in element.items():
                    if k.startswith("type_") and v == 1:
                        element_type = k.replace("type_", "")
                        break  # Found the element type

                if not element_type:
                    continue  # Skip if no type is found

                print(f"Checking {element_type} at ({x}, {y}), Size: {width}x{height}")  # Debugging

                # Only check interactive elements
                if element_type not in ["button", "input", "dropdown", "checkbox", "link"]:
                    continue  # Ignore non-interactive elements

                # Check if the element is off-screen
                if x + width <= 0 or y + height <= 0 or x >= screen_width or y >= screen_height:
                    feedback.append(f"The {element_type} at ({x}, {y}) is off-screen and should be repositioned.")

                # Check if the element is too small (example: width or height < 10% of screen width)
                if width < 0.1 * screen_width or height < 0.1 * screen_height:
                    feedback.append(f"The {element_type} at ({x}, {y}) is too small ({width}px × {height}px). Consider increasing its size.")

        # Only add this message if no issues were found
        if not feedback:
            feedback.append("All interactive elements are visible and properly sized.")

        return feedback 

    def visible_instructions(self, elements_data):
        # Does the UI provide tooltips, placeholders, or labels?
        has_missing_instructions = False

        for group_id, elements in elements_data.items():
            for element in elements:
                if not isinstance(element, dict): 
                    continue 
                element_type = None

                # Identify the element type based on type_* keys
                for key, value in element.items():
                    if key.startswith("type_") and value == 1:
                        element_type = key.replace("type_", "")

                if not element_type:
                    continue  # Skip if no valid type is found

                # Simulating placeholders, tooltips, or labels (if available)
                tooltip = element.get("tooltip", None)
                placeholder = element.get("placeholder", None)
                label = element.get("label", None)

                print(f"Checking {element_type} for instructions...")  # Debugging

                # Only check interactive elements
                if element_type not in ["oval", "rectangle", "text", "symbolInstance"]:
                    continue  # Ignore non-interactive elements

                # Check if any instruction is provided
                if not tooltip and not placeholder and not label:
                    has_missing_instructions = True  # Mark issue found
                    break  # Stop checking further elements after finding one issue

        # Provide a single feedback message
        if has_missing_instructions:
            return ["Some interactive elements are missing instructions (tooltip, placeholder, or label). Consider adding them."]
        
        return ["All interactive elements have visible instructions."]

    def consistent_navigation(self, elements_data):
        # Consistency in Navigation
        navigation_elements = ["type_symbolInstance", "type_rectangle", "type_text", "type_triangle", "type_group"]       
        screen_nav_elements = {}  # Store element types per screen/group
        feedback = []

        for group_id, elements in elements_data.items():
            if not isinstance(elements, list):  # Skip invalid groups
                continue
            
            screen_nav_elements[group_id] = set()  # Track elements for this group

            for element in elements:
                if not isinstance(element, dict):  # Ensure valid data
                    continue

                for key, value in element.items():
                    if key.startswith("type_") and value == 1:
                        element_type = key.replace("type_", "")
                        if element_type in navigation_elements:
                            screen_nav_elements[group_id].add(element_type)

        # Compare navigation elements across screens
        reference_screen = next(iter(screen_nav_elements.values()), set())  # Get the first screen as reference

        for screen_id, elements in screen_nav_elements.items():
            if elements != reference_screen:
                feedback.append(f"Inconsistent navigation elements in screen {screen_id}. Expected: {reference_screen}, Found: {elements}")

        if not feedback:
            feedback.append("Navigation elements are consistent across screens.")

        return feedback

    def evaluate_icon_labeling(self, is_icon_labeled):
        if is_icon_labeled:
            return "Your icons are labeled - Good Recognition"
        else: return "Your icons are not labeled - Try Labeling your icons for a better recognition"
    
    def evaluate_icon_size(self, icon_width, icon_height):
        # icons = [element for element in elements if element['type'] == 'symbolInstance']
        # Check if icon is too small (threshold: 24px width/height)
        if icon_width < 24 or icon_height < 24:
            return "Your icons too small - Try increasing your icon size"
        elif icon_width > 32 or icon_height > 32:
            return "Your icons too large - Try decreasing your icon size"

    def evaluate_rule(self, is_icon_labeled, icon_width, icon_height):
        feedback = []

        # Step 1: Evaluate labeled icons
        icon_labeling_feedback = self.evaluate_icon_labeling(is_icon_labeled)
        feedback.append(f"Icon Labeling: {icon_labeling_feedback}")

        # Step 2: Evaluate icons size
        icon_size_feedback = self.evaluate_icon_size(icon_width, icon_height)
        feedback.append(f"Icon Size: {icon_size_feedback}")

        #     # Step 2: Evaluate element count
        #     num_elements = len(elements['elements'])
        #     element_count_feedback = self.evaluate_elements_count(num_elements)
        #     if element_count_feedback:
        #         feedback.append(element_count_feedback)
        # else:
        #     feedback.append(f"White Space Ratio follows minimalistic rule")
        #     feedback.append(f"Number of elements follows minimalistic rule")

        # # Step 3: Check for irrelevant elements
        # irrelevant_elements = [el for el in elements['elements'] if self.is_irrelevant(el)]
        # if irrelevant_elements:
        #     feedback.append(f"This design contains {len(irrelevant_elements)} irrelevant elements. Consider removing them.")
        # else:
        #     feedback.append(f"No irrelevant elements. Elements follow minimalistic rule")

        # # If no feedback, mention adherence to minimalist rule
        # if not feedback:
        #     feedback.append("Design adheres to the minimalist rule.")

        # self.condition = 0
        # print(feedback)

        return feedback
        
