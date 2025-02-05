import pandas as pd
from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface 

class Minimalist(HeuristicInterface):
    def __init__(self, clusters_data, max_elements=10, min_elements=3):
        self.clusters_data = clusters_data
        self.max_elements = max_elements
        self.min_elements = min_elements

    def calculate_white_space_ratio(self, elements, screen_width, screen_height):
        if screen_width <= 0 or screen_height <= 0:
            print("Invalid screen dimensions. Returning 0.")
            return 0
        total_element_area = 0
        screen_area = screen_width * screen_height

        for element in elements['elements']:
            width = element.get('width')
            height = element.get('height')
            if isinstance(width, (int, float)) and isinstance(height, (int, float)):
                element_area = width * height

            # Exclude backgrounds
            if element_area < screen_area:  
                total_element_area += element_area 
        # Compute white space ratio
        white_space_ratio = 1 - (total_element_area / screen_area)  
        return max(0, white_space_ratio)  # Ensure it's not negative

    def evaluate_minimalist(self, elements, screen_width, screen_height):
        # Call the white space ratio check
        white_space_ratio = self.calculate_white_space_ratio(elements, screen_width, screen_height)
        if white_space_ratio >= 0.4:
            return white_space_ratio, "Pass - Minimalist Design"
        else:
            return white_space_ratio, "Fail - Cluttered Design"

    def evaluate_rule(self):
        feedback = []
        for cluster_id, elements in self.clusters_data.items():
            num_elements = len(elements)
            
            # Check total number of elements
            if num_elements > self.max_elements:
                feedback.append(f"Cluster {cluster_id}: Too many elements ({num_elements}). Consider removing unnecessary elements.")
            elif num_elements < self.min_elements:
                feedback.append(f"Cluster {cluster_id}: Too few elements ({num_elements}). Consider adding more essential elements.")
            
            # Check for irrelevant elements
            irrelevant_elements = [el for el in elements if self.is_irrelevant(el)]
            if irrelevant_elements:
                feedback.append(f"Cluster {cluster_id}: Contains {len(irrelevant_elements)} irrelevant elements. Consider removing them.")
        
        return feedback if feedback else ["Design adheres to the minimalist rule."]
    
    def is_irrelevant(self, element):
        # In this case, an element may be considered irrelevant if it has no text and is not a primary shape.
        return (
            element.get("type_text", 0) == 0 and  
            element.get("type_symbolInstance", 0) == 0 and
            element.get("type_rectangle", 0) == 0 and 
            element.get("type_oval", 0) == 0
        )




    # def identify_irrelevant_elements(self, cluster_data):
    #     # Count occurrences of each element type
    #     element_counts = cluster_data["type"].value_counts()

    #     # Define thresholds for rare and frequent elements (adjustable)
    #     min_threshold = 2  # Elements appearing less than this might be rare
    #     max_threshold = 50  # Elements appearing more than this might be clutter

    #     # Detect rare and frequent elements
    #     rare_elements = element_counts[element_counts < min_threshold].index.tolist()
    #     frequent_elements = element_counts[element_counts > max_threshold].index.tolist()

    #     feedback = {}
    #     if rare_elements:
    #         feedback["rare_elements"] = f"These element types appear too infrequently: {rare_elements}. Consider reviewing their necessity."
    #     if frequent_elements:
    #         feedback["frequent_elements"] = f"These element types appear too frequently: {frequent_elements}. Consider reducing repetition."

    #     if not feedback:
    #         return "No irrelevant elements detected based on frequency."

    #     return feedback
