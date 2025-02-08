from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface 


class Recognition(HeuristicInterface):

    def __init__(self):
        pass

    def minimized_memory_load(self, elements):
        #  Are interactive elements visible instead of hidden?
        feedback = []

        for _, element in elements.iterrows():
            x = element["position.x"]
            y = element["position.y"]
            width = element["width"]
            height = element["height"]

            screen_width = element["screen_width"]
            screen_height = element["screen_height"]

            element_type = element["type"]

            print(f"Checking {element_type} at ({x}, {y}), Size: {width}x{height}")  # Debugging

            # Only check interactive elements
            if element_type not in ["button", "input", "dropdown", "checkbox", "link"]:
                continue    # Ignore non-interactive elements

            # Check if the element is off-screen
            if x + width <= 0 or y + height <= 0 or x >= screen_width or y >= screen_height:
                feedback.append(f"The {element_type} at ({x}, {y}) is off-screen and should be repositioned.\n")
                continue

            # Check if the element is too small (example: width or height < 10 pixels)
            if width < 10 or height < 10:
                feedback.append(f"The {element_type} at ({x}, {y}) is too small ({width}px × {height}px). Consider increasing its size.\n")
                continue

            # If no issues found, return a positive message
            if not feedback:
                feedback.append("All interactive elements are visible and properly sized.")

            return feedback




    def evaluate_rule(self, cluster_data):
        pass
