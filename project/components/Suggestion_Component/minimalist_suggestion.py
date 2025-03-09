from components.Heuristics_Component.heuristic_rules.minimalist import Minimalist
from components.Suggestion_Component.suggestion import SuggestionInterface

class MinimalistSuggestions(SuggestionInterface):
    def __init__(self, minimalist=None):
        self.minimalist = minimalist if minimalist else Minimalist()

    def suggest_white_space_fixes(self, elements, screen_width, screen_height, white_space_ratio):
        if white_space_ratio >= 0.35:
            return []

        # Find the largest element (excluding full-screen backgrounds)
        largest = max(
            [el for el in elements['elements'] if el.get('width') * el.get('height') < screen_width * screen_height],
            key=lambda el: el.get('width') * el.get('height'),
            default=None
        )
        largest_idx = elements['elements'].index(largest) if largest else -1
        suggestions = [
            {
                "text": 'Reduce the largest element by 20%',
                "action": {
                    "type": "resize",
                    "index": largest_idx,
                    "width": largest['width'] * 0.8 if largest else 0,
                    "height": largest['height'] * 0.8 if largest else 0
                }
            },
            {
                "text": "Increase spacing between elements by 10px",
                "action": {
                    "type": "adjust_spacing",
                    "spacing": 10
                }
            }
        ]
        return suggestions