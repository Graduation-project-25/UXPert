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

        return feedback  # Return after checking all elements

    # def visible_instructions(self):

    def evaluate_rule(self, cluster_data):
        pass
