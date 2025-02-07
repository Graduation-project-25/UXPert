from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface 


class Minimalist(HeuristicInterface):
    def __init__(self, max_elements=10, min_elements=3):
        self.max_elements = max_elements
        self.min_elements = min_elements
        self.condition = 0

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
        if white_space_ratio < 0.36:
            self.condition += 1 
        return max(0, white_space_ratio)  # Ensure it's not negative

    def evaluate_white_space_ratio(self, elements, screen_width, screen_height):
        # Call the white space ratio check
        white_space_ratio = self.calculate_white_space_ratio(elements, screen_width, screen_height)
        if white_space_ratio >= 0.35:
            return white_space_ratio, "Good White space Ratio"
        else:
            return white_space_ratio, "Cluttered Design - Try to increase the white space between elements in your design"

    def evaluate_elements_count(self, num_elements):
        if num_elements > self.max_elements:
            return f"This screen has too many elements ({num_elements}). Consider removing unnecessary elements."
        elif num_elements < self.min_elements:
            self.condition += 1 
            return f"This screen has too few elements ({num_elements}). Consider adding more essential elements."
        return None

    def is_irrelevant(self, element):
        # Checks if an element is irrelevant (e.g., no text and not a primary shape). """
        # In this case, an element may be considered irrelevant if it has no text and is not a primary shape.
        return (
            element.get("type_text", 0) == 0 and  
            element.get("type_symbolInstance", 0) == 0 and
            element.get("type_rectangle", 0) == 0 and 
            element.get("type_oval", 0) == 0
        )

    def evaluate_rule(self, elements, screen_width, screen_height):
        feedback = []

        # If the white space ratio is low and the number of elements is small consider it minimalistic 
        if self.condition != 2:
            # Step 1: Evaluate white space ratio
            white_space_ratio, white_space_feedback = self.evaluate_white_space_ratio(elements, screen_width, screen_height)
            feedback.append(f"White Space Ratio: {white_space_ratio:.2f} - {white_space_feedback}")

            # Step 2: Evaluate element count
            num_elements = len(elements['elements'])
            element_count_feedback = self.evaluate_elements_count(num_elements)
            if element_count_feedback:
                feedback.append(element_count_feedback)

        # Step 3: Check for irrelevant elements
        irrelevant_elements = [el for el in elements['elements'] if self.is_irrelevant(el)]
        if irrelevant_elements:
            feedback.append(f"This design contains {len(irrelevant_elements)} irrelevant elements. Consider removing them.")

        # If no feedback, mention adherence to minimalist rule
        if not feedback:
            feedback.append("Design adheres to the minimalist rule.")

        return feedback
        



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