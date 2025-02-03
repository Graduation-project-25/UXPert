import pandas as pd 


from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Minimalist(HeuristicInterface):
    def evaluate_rule(self,cluster_data):
        print("Minimalist Rule")

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
    
    def whitespace_ratio(self, cluster_data):
        screen_area = 0


