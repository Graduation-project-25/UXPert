import pandas as pd 


from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Minimalist(HeuristicInterface):

    def __init__(self, max_elements_threshold=50, min_elements_threshold=5, screen_irrelevant_elements=None):
        self.max_elements_threshold = max_elements_threshold
        self.min_elements_threshold = min_elements_threshold
        self.screen_irrelevant_elements = screen_irrelevant_elements if screen_irrelevant_elements else {}

    def count_ui_elements(self, elements, threshold_min=3, threshold_max=10):
        # Ensure elements is a list or a DataFrame and extract rows count
        if isinstance(elements, pd.DataFrame):
            count = elements.shape[0]  # Get number of rows
        elif isinstance(elements, list):
            count = len(elements)
        else:
            raise TypeError(f"Unsupported type {type(elements)} for count_ui_elements")
        
        if count < threshold_min:
            status = 'Too Few - Screen might be too empty'
        elif count > threshold_max:
            status = 'Too Many - Needs reduction'
        else:
            status = 'Balanced - Design is optimal'
        
        return count, status

    def check_element_count(self, cluster_data):
        num_elements = len(cluster_data)

        if num_elements > self.max_elements_threshold:
            return f"Too many elements ({num_elements}). Consider simplifying the design."
        elif num_elements < self.min_elements_threshold:
            return f"Too few elements ({num_elements}). Consider adding essential components."
        return "Element count is well-balanced."

    def numberOfElements(self, cluster_data):
        num_elements = len(cluster_data) # Count total elements

        # Detect redundant elements (e.g., multiple buttons with the same name)
        element_types = {}
        for element in cluster_data:
            element_type = element.get('type', 'Unknown')
            element_types[element_type] = element_types.get(element_type, 0) + 1

        # More than 3 similar elements
        redundant_elements = {k: v for k, v in element_types.items() if v > 3}

        # Generate feedback
        feedback = {}

        if num_elements > max_elements:
            feedback["cluster_warning"] = f"Too many elements ({num_elements}). Consider simplifying the design."

        if redundant_elements:
            feedback["redundant_elements"] = f"Repetitive elements detected: {redundant_elements}. Try reducing similar elements."
        
        if not feedback:
            feedback["status"] = "The design follows the minimalism principle."

        return feedback
    
    def calculate_white_space_ratio(self, design_json, screen_width, screen_height):
        screen_area = screen_width * screen_height
        total_element_area = 0

        for element in design_json["elements"]:
            width, height = element["width"], element["height"]
            total_element_area += width * height  # Sum up all element areas

        wsr = 1 - (total_element_area / screen_area)  # Compute white space ratio
        return wsr


    def evaluate_rule(self,design_json, screen_width, screen_height):
        wsr = self.calculate_white_space_ratio(design_json, screen_width, screen_height)

        if wsr >= 0.4:
            return "Pass - Minimalist Design"  
        else:
            return "Fail - Cluttered Design"  
