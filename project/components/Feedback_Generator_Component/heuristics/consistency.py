import numpy as np
import pandas as pd
from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

# Step 1: Define the Consistency class to evaluate the heuristic
class Consistency(HeuristicInterface):

    def evaluate_rule(self, cluster_data):
        """
        Evaluates the consistency of a cluster based on:
        1. Similar elements with the same size having the same color.
        2. Alignment (horizontal/vertical).
        3. Proportional sizes of elements.
        """
        # Ensure `cluster_data` is in a proper DataFrame format
        if not isinstance(cluster_data, pd.DataFrame):
            raise TypeError("cluster_data must be a pandas DataFrame")
        
        # Calculate the individual scores
        color_consistency_score = self.check_color_consistency(cluster_data)
        alignment_consistency_score = self.calculate_alignment_consistency(cluster_data)
        size_proportionality_score = self.check_size_proportionality(cluster_data)

        # Combine scores with respective weights
        total_consistency_score = (
            0.4 * color_consistency_score +
            0.3 * alignment_consistency_score +
            0.3 * size_proportionality_score
        )

        return {
            "ColorConsistency": round(color_consistency_score * 100, 2),
            "AlignmentConsistency": round(alignment_consistency_score * 100, 2),
            "SizeProportionality": round(size_proportionality_score * 100, 2),
            "TotalConsistency": round(total_consistency_score * 100, 2)
        }

    def check_color_consistency(self, cluster_data):
        """
        Checks if elements with the same size in a cluster have the same color.
        """
        # Group the data based on width and height
        size_groups = cluster_data.groupby(['width', 'height'])
        total_groups = len(size_groups)
        
        # Count how many groups have consistent colors
        consistent_groups = sum(
            1 for _, group in size_groups 
            if group[['color_r', 'color_g', 'color_b']].drop_duplicates().shape[0] == 1
        )

        # Return the consistency ratio
        return consistent_groups / total_groups if total_groups > 0 else 1.0

    def check_size_proportionality(self, cluster_data):
        """
        Evaluates the proportionality of element sizes within the cluster.
        """
        # Calculate the area of each element (width * height)
        sizes = cluster_data['width'] * cluster_data['height']
        size_std_dev = np.std(sizes)  # Standard deviation to measure variation
        return 1 / (1 + size_std_dev)  # Return inverse of the variation

    def calculate_alignment_consistency(self, cluster_data):
        """
        Measures how well elements are aligned either horizontally or vertically.
        """
        x_positions = cluster_data['position.x'].values
        y_positions = cluster_data['position.y'].values

        # Calculate the variance in x and y positions
        horizontal_alignment = np.var(x_positions)
        vertical_alignment = np.var(y_positions)

        # Return a score based on alignment
        return 1 / (1 + horizontal_alignment + vertical_alignment)

# Step 2: Function to convert extracted feature data into a DataFrame (for evaluation)
def prepare_data_for_evaluation(extracted_features):
    """
    Converts the extracted features (width, height, color, position) into a pandas DataFrame.
    """
    data = {
        'width': extracted_features['width'],
        'height': extracted_features['height'],
        'color_r': extracted_features['color_r'],
        'color_g': extracted_features['color_g'],
        'color_b': extracted_features['color_b'],
        'position.x': extracted_features['position_x'],
        'position.y': extracted_features['position_y']
    }
    return pd.DataFrame(data)

# Step 3: Example usage of the Consistency class with your extracted features
def evaluate_ui_elements(extracted_features):
    """
    Evaluates the UI elements using the Consistency heuristic.
    """
    # Prepare the data
    cluster_data = prepare_data_for_evaluation(extracted_features)
    
    # Initialize the Consistency heuristic evaluator
    consistency_evaluator = Consistency()

    # Evaluate the consistency of the cluster
    consistency_scores = consistency_evaluator.evaluate_rule(cluster_data)

    return consistency_scores


