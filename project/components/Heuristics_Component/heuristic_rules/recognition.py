from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface 

class Recognition(HeuristicInterface):

    def __init__(self):
        pass

    def minimized_memory_load(self, element, element_type, screen_width, screen_height):
        # Checks if an element is off-screen or too small
        feedback = []
        x = element.get("position.x", 0)
        y = element.get("position.y", 0)
        width = element.get("width", 0)
        height = element.get("height", 0)

        if element_type not in ["button", "input", "dropdown", "checkbox", "link"]:
            return feedback

        if x + width <= 0 or y + height <= 0 or x >= screen_width or y >= screen_height:
            feedback.append(f"The {element_type} at ({x}, {y}) is off-screen and should be repositioned.")
        if width < 0.1 * screen_width or height < 0.1 * screen_height:
            feedback.append(f"The {element_type} at ({x}, {y}) is too small ({width}px × {height}px). Consider increasing its size.")

        return feedback

    def visible_instructions(self, element, element_type):
        # Does the UI provide tooltips, placeholders, or labels?
        if element_type not in ["oval", "rectangle", "text", "symbolInstance"]:
            # return "Element type not applicable for instruction check."
            return

        tooltip = element.get("tooltip", None)
        placeholder = element.get("placeholder", None)
        label = element.get("label", None)

        if tooltip is None and placeholder is None and label is None:
            return "Missing instructions (tooltip, placeholder, or label). Consider adding them."
        else:
            return "Element has visible instructions."

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

    def evaluate_rule(self, element, element_type, screen_width, screen_height, is_icon_labeled, icon_width, icon_height):
        feedback = []

        # Step 1: Evaluate memory load
        memory_load_feedback = self.minimized_memory_load(element, element_type, screen_width, screen_height)
        if (memory_load_feedback != ""):
            feedback.append(memory_load_feedback)
        # if not memory_load_feedback:
        #     feedback.append("All interactive elements are visible and properly sized.")

        # Step 2: Evaluate instruction
        visible_instructions_feedback = self.visible_instructions(element, element_type)
        if (visible_instructions_feedback != ""):
            feedback.append(visible_instructions_feedback)

        # Step 3: Evaluate labeled icons and size if it is an icon.
        # if is_icon:
        icon_labeling_feedback = self.evaluate_icon_labeling(is_icon_labeled)
        feedback.append(f"Icon Labeling: {icon_labeling_feedback}")

    # Step 4: Evaluate icons size
        icon_size_feedback = self.evaluate_icon_size(icon_width, icon_height)
        feedback.append(f"Icon Size: {icon_size_feedback}")

        # If no feedback, mention adherence to Recognition rule
        if not feedback:
            feedback.append("Design adheres to the Recognition rule.")

        return feedback


