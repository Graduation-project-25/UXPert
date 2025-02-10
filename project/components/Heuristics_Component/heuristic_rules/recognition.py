import json
import math
import os
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface 


class Recognition(HeuristicInterface):

    def __init__(self):
        pass

    def minimized_memory_load(self, elements):
        #  Are interactive elements visible instead of hidden?
        # visibility_status = []
        feedback = []

        for _, element in elements.iterrows():
            x = element["position.x"]
            y = element["position.y"]
            width = element["width"]
            height = element["height"]

            screen_width = element["screen_width"]
            screen_height = element["screen_height"]

            element_type = element["type"]

            # Only check interactive elements
            if element_type not in ["button", "input", "dropdown", "checkbox", "link"]:
                # visibility_status.append("Not Interactive")
                # Ignore them
                continue

            # Check if the element is off-screen
            if x + width <= 0 or y + height <= 0 or x >= screen_width or y >= screen_height:
                # visibility_status.append("Off-screen")
                feedback += f"The {element_type} at ({x}, {y}) is off-screen and should be repositioned.\n"
                continue

            # Check if the element is too small (example: width or height < 10 pixels)
            if width < 10 or height < 10:
                # visibility_status.append("Too Small")
                feedback += f"The {element_type} at ({x}, {y}) is too small ({width}px × {height}px). Consider increasing its size.\n"
                continue

            # If no issues found, mark as "Visible"
            # visibility_status.append("Visible")

            # Add results to the dataframe
            # cluster_data["visibility_status"] = visibility_status
            # return df

            # If no issues found, return a positive message
            if not feedback:
                return "All interactive elements are visible and properly sized."

            return feedback


    def evaluate_icon_abeling(self, is_icon_labeled):
        if is_icon_labeled:
            return "Your icons are labeled - Good Recognition"
        else: return "Your icons are not labeled - Try Labeling your icons for a better recognition"
    
    def evaluate_icon_size(self, elements):
        icons = [element for element in elements if element['type'] == 'symbolInstance']
        for icon in icons:
            # Check if icon is too small (threshold: 24px width/height)
            if icon.get('width', 0) < 24 or icon.get('height', 0) < 24:
                return "Your icons too small - Try increasing your icon size"
            elif icon.get('width', 0) > 32 or icon.get('height', 0) > 32:
                return "Your icons too large - Try decreasing your icon size"









    def evaluate_rule(self, cluster_data):
        pass

