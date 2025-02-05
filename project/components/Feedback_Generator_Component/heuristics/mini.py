import pandas as pd
from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Minimalist(HeuristicInterface):
    def __init__(self, clusters_data, max_elements=10, min_elements=3):
        """
        Initialize the Minimalist heuristic.
        :param clusters_data: Dictionary containing cluster information.
        :param max_elements: Maximum recommended number of elements per screen.
        :param min_elements: Minimum recommended number of elements per screen.
        """
        self.clusters_data = clusters_data
        self.max_elements = max_elements
        self.min_elements = min_elements
    
    def evaluate_rule(self):
        """
        Evaluate the design based on the minimalist rule.
        """
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
        """
        Determine if an element is irrelevant.
        In this case, an element may be considered irrelevant if it has no text and is not a primary shape.
        """
        return (
            element.get("type_text", 0) == 0 and  
            element.get("type_symbolInstance", 0) == 0 and
            element.get("type_rectangle", 0) == 0 and 
            element.get("type_oval", 0) == 0
        )
