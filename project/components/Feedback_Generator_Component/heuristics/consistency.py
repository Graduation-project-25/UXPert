import numpy as np
import pandas as pd
from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Consistency(HeuristicInterface):
    
    def prepare_data_for_evaluation(self, extracted_features):
        """
        Converts the extracted features (width, height, color, position) into a pandas DataFrame.
        Handles missing values by filling them with defaults (0 or NaN).
        """
        # Fill missing values with NaN or default values
        data = {
            'width': extracted_features.get('width', [0] * len(extracted_features.get('width', []))),
            'height': extracted_features.get('height', [0] * len(extracted_features.get('height', []))),
            'color_r': extracted_features.get('color_r', [0] * len(extracted_features.get('color_r', []))),
            'color_g': extracted_features.get('color_g', [0] * len(extracted_features.get('color_g', []))),
            'color_b': extracted_features.get('color_b', [0] * len(extracted_features.get('color_b', []))),
            'position.x': extracted_features.get('position_x', [0] * len(extracted_features.get('position_x', []))),
            'position.y': extracted_features.get('position_y', [0] * len(extracted_features.get('position_y', [])))
        }
        
        return pd.DataFrame(data)

    def check_color_consistency(self, cluster_data):
        """
        Check for color consistency between similar-sized elements.
        Returns a score based on the degree of consistency.
        """
        # Group elements by size (width and height)
        cluster_data['size'] = cluster_data['width'] * cluster_data['height']
        similar_size_groups = cluster_data.groupby('size')
        
        color_consistency_score = 0
        num_groups = len(similar_size_groups)
        
        for _, group in similar_size_groups:
            unique_colors = group[['color_r', 'color_g', 'color_b']].drop_duplicates()
            if len(unique_colors) == 1:
                color_consistency_score += 1  # Consistent color for all elements in this size group
            else:
                color_consistency_score += 0.5  # Partially consistent or inconsistent colors
        
        return color_consistency_score / num_groups if num_groups > 0 else 0

    def calculate_alignment_consistency(self, cluster_data):
        """
        Measures how well elements are aligned either horizontally or vertically.
        You can adjust weights for horizontal and vertical alignment.
        """
        x_positions = cluster_data['position.x'].values
        y_positions = cluster_data['position.y'].values

        # Calculate the variance in x and y positions
        horizontal_alignment = np.var(x_positions)
        vertical_alignment = np.var(y_positions)

        # Adjust horizontal and vertical alignment weight
        horizontal_weight = 0.6  # Adjust this based on importance in your design
        vertical_weight = 0.4    # Adjust this based on importance in your design

        # Weighted alignment score
        alignment_score = 1 / (1 + (horizontal_weight * horizontal_alignment + vertical_weight * vertical_alignment))

        return alignment_score

    def check_size_proportionality(self, cluster_data):
        """
        Evaluates the proportionality of element sizes within the cluster.
        Adds a threshold to define the acceptable range of size variation.
        """
        # Calculate the area of each element (width * height)
        sizes = cluster_data['width'] * cluster_data['height']
        size_std_dev = np.std(sizes)  # Standard deviation to measure variation

        # Define a threshold for acceptable size variation
        size_threshold = 50  # Example threshold; tweak it according to your needs
        return max(0, 1 - size_std_dev / size_threshold)  # Normalize based on the threshold

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
        
        # Check for the necessary columns
        required_columns = ['width', 'height', 'color_r', 'color_g', 'color_b', 'position.x', 'position.y']
        missing_columns = [col for col in required_columns if col not in cluster_data.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

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

        # Detailed feedback
        feedback = {
            "ColorConsistency": round(color_consistency_score * 100, 2),
            "AlignmentConsistency": round(alignment_consistency_score * 100, 2),
            "SizeProportionality": round(size_proportionality_score * 100, 2),
            "TotalConsistency": round(total_consistency_score * 100, 2),
            "Feedback": {
                "ColorConsistency": "Colors are consistent across similar-sized elements."
                if color_consistency_score > 0.9 else "Colors are inconsistent for some similar-sized elements.",
                "AlignmentConsistency": "Elements are well-aligned horizontally and vertically."
                if alignment_consistency_score > 0.9 else "Alignment needs improvement.",
                "SizeProportionality": "The size variation is within acceptable limits."
                if size_proportionality_score > 0.8 else "Size proportionality is off, consider adjusting element sizes."
            }
        }

        return feedback
