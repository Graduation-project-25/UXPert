import pandas as pd 
import pandas as pd 


import pandas as pd  


from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Minimalist(HeuristicInterface):

    def __init__(self, max_elements_threshold=50, min_elements_threshold=5):
        self.max_elements_threshold = max_elements_threshold
        self.min_elements_threshold = min_elements_threshold

    def calculate_white_space_ratio(self, design_json, screen_width, screen_height):
        screen_area = screen_width * screen_height
        total_element_area = 0

        for element in design_json["elements"]:
            width, height = element["width"], element["height"]
            total_element_area += width * height  # Sum up all element areas

        wsr = 1 - (total_element_area / screen_area)  # Compute white space ratio
        return wsr

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

        if num_elements > self.max_elements_threshold:
            feedback["cluster_warning"] = f"Too many elements ({num_elements}). Consider simplifying the design."

        if redundant_elements:
            feedback["redundant_elements"] = f"Repetitive elements detected: {redundant_elements}. Try reducing similar elements."

        if not feedback:
            feedback["status"] = "The design follows the minimalism principle."

        return feedback
    
    def infer_screen_type(self, screen_data):
        width = screen_data["screen_size"]["screen_width"]
        height = screen_data["screen_size"]["screen_height"]
        elements = screen_data["elements"]

        # Threshold to determine if a screen is scrollable
        scroll_threshold = 2.5  # Adjust based on dataset characteristics

        # Calculate text density
        text_elements = [el for el in elements if el["type"] == "text"]
        text_ratio = len(text_elements) / len(elements) if elements else 0

        # Calculate media density (includes various visual elements)
        media_elements = [el for el in elements if el["type"] in ["bitmap", "image", "video", "graphic"]]
        media_ratio = len(media_elements) / len(elements) if elements else 0

        # Determine screen type
        if height / width > scroll_threshold:
            return "long_scrollable_screen"
        elif text_ratio > 0.6:  # More than 60% of elements are text
            return "text_heavy_screen"
        elif media_ratio > 0.4:  # More than 40% are media elements
            return "media_screen"
        else:
            return "generic_screen"

    def identify_irrelevant_elements(self, cluster_data):
        # Count occurrences of each element type
        element_counts = cluster_data["type"].value_counts()

        # Define thresholds for rare and frequent elements (adjustable)
        min_threshold = 2  # Elements appearing less than this might be rare
        max_threshold = 50  # Elements appearing more than this might be clutter

        # Detect rare and frequent elements
        rare_elements = element_counts[element_counts < min_threshold].index.tolist()
        frequent_elements = element_counts[element_counts > max_threshold].index.tolist()

        feedback = {}
        if rare_elements:
            feedback["rare_elements"] = f"These element types appear too infrequently: {rare_elements}. Consider reviewing their necessity."
        if frequent_elements:
            feedback["frequent_elements"] = f"These element types appear too frequently: {frequent_elements}. Consider reducing repetition."

        if not feedback:
            return "No irrelevant elements detected based on frequency."

        return feedback

    def whitespace_ratio(self, cluster_data):
        screen_area = 0

    def evaluate_rule(self,design_json, screen_width, screen_height):
        wsr = self.calculate_white_space_ratio(design_json, screen_width, screen_height)

        if wsr >= 0.4:
            return "Pass - Minimalist Design"  
        else:
            return "Fail - Cluttered Design"  
