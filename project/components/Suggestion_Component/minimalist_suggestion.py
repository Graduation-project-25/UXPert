from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist
from components.Suggestion_Component.suggestion import SuggestionInterface

class MinimalistSuggestions:
    def __init__(self, minimalist_instance):
        self.minimalist = minimalist_instance
        self.suggestions = []
        
    def generate_suggestion(self, elements, screen_width, screen_height):
        """
        Generates suggestions for improving whitespace ratio if it's below the threshold.
        Returns a list of suggestion strings.
        """
        self.suggestions = []

        # Evaluate whitespace ratio using the Minimalist class
        white_space_ratio, feedback, failed = self.minimalist.evaluate_white_space_ratio(elements, screen_width, screen_height)

        if failed and "Cluttered Design - Try increasing the white space between elements in your design" in feedback:
            # Suggestion 1: Increase padding between all elements by 20%
            self.suggestions.append("Increase padding between all elements by 20% to improve whitespace.")

            # Suggestion 2: Reduce element sizes by 15% to create more whitespace
            self.suggestions.append("Reduce the size of all elements by 15% to create more whitespace.")

        return self.suggestions

    def apply_suggestion(self, suggestion_index, elements):
        """
        Applies the chosen suggestion to modify the elements.
        Returns the modified elements list.
        """
        if not self.suggestions or suggestion_index < 0 or suggestion_index >= len(self.suggestions):
            return elements  # No valid suggestion, return unchanged elements

        suggestion = self.suggestions[suggestion_index]

        if "Increase padding" in suggestion:
            return self._increase_padding(elements)
        elif "Reduce the size" in suggestion:
            return self._reduce_element_sizes(elements)
        else:
            return elements  # No action if suggestion not recognized

    def _increase_padding(self, elements):
        """
        Increases the padding (spacing) between all elements by shifting them.
        Assumes elements have x, y, width, and height attributes.
        """
        modified_elements = elements['elements'][:]  # Create a copy of the list

        for element in modified_elements:
            # Check if required fields exist
            if 'x' in element and 'y' in element and 'width' in element and 'height' in element:
                # Increase position to simulate more padding (e.g., move right and down by 20% of width/height)
                padding_increase = 20  # Fixed increase in pixels for simplicity
                element['x'] = element['x'] + padding_increase
                element['y'] = element['y'] + padding_increase

                # Optionally reduce size to maintain balance
                if element['width'] > padding_increase * 2:
                    element['width'] = element['width'] - padding_increase
                if element['height'] > padding_increase * 2:
                    element['height'] = element['height'] - padding_increase

        return {'elements': modified_elements}

    def _reduce_element_sizes(self, elements):
        """
        Reduces the size of all elements by 15% to create more whitespace.
        """
        modified_elements = elements['elements'][:]  # Create a copy of the list

        for element in modified_elements:
            if 'width' in element and 'height' in element:
                # Reduce size by 15% (integer-based)
                reduction = 15  # Fixed reduction percentage converted to integer effect
                element['width'] = element['width'] * (100 - reduction) // 100
                element['height'] = element['height'] * (100 - reduction) // 100

                # Ensure sizes don't go below 1 (minimum size)
                element['width'] = max(1, element['width'])
                element['height'] = max(1, element['height'])

        return {'elements': modified_elements}