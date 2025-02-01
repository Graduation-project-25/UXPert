from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Minimalist(HeuristicInterface):
    def evaluate_rule(self,cluster_data):
        print("Minimalist Rule")

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

# For test only (to be removed)
# # Example Usage
# cluster_data = [
#     {"type": "button", "name": "Submit", "position": {"x": 50, "y": 100}, "width": 100, "height": 50},
#     {"type": "button", "name": "Submit", "position": {"x": 200, "y": 100}, "width": 100, "height": 50},
#     {"type": "button", "name": "Submit", "position": {"x": 350, "y": 100}, "width": 100, "height": 50},
#     {"type": "button", "name": "Submit", "position": {"x": 500, "y": 100}, "width": 100, "height": 50},
#     {"type": "text", "name": "Title", "position": {"x": 50, "y": 200}, "width": 200, "height": 50},
# ]

# print(numberOfElements(None, cluster_data))