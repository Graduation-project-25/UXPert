import numpy as np

from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Consistency(HeuristicInterface):

    # def __init__(self, color_weight=0.4, alignment_weight=0.3, size_weight=0.3):
    #     self.color_weight = color_weight
    #     self.alignment_weight = alignment_weight
    #     self.size_weight = size_weight

    def evaluate_rule(self,cluster_data):
        """
        Evaluates the consistency of a cluster based on:
        1. Similar elements with the same size having the same color.
        2. Alignment (horizontal/vertical).
        3. Proportional sizes of elements.
        """
        # Check Color Consistency
        color_consistency_score = self.check_color_consistency(cluster_data)

        # Check Alignment Consistency
        alignment_consistency_score = self.calculate_alignment_consistency(cluster_data)

        # Check Size Proportionality
        size_proportionality_score = self.check_size_proportionality(cluster_data)

        # Aggregate Consistency Score
        total_consistency_score = (
            0.4 * color_consistency_score +
            0.3 * alignment_consistency_score +
            0.3 * size_proportionality_score
        )

        # Convert scores to percentages
        return {
            "ColorConsistency": round(color_consistency_score * 100, 2),
            "AlignmentConsistency": round(alignment_consistency_score * 100, 2),
            "SizeProportionality": round(size_proportionality_score * 100, 2),
            "TotalConsistency": round(total_consistency_score * 100, 2)
        }


    def check_color_consistency(self,cluster_data):
        """
        Checks if elements with the same size in a cluster have the same color.
        """
        size_groups = cluster_data.groupby(['width', 'height'])
        total_groups = len(size_groups)
        consistent_groups = 0

        for _, group in size_groups:
            unique_colors = group[['color_r', 'color_g', 'color_b']].drop_duplicates().shape[0]
            if unique_colors == 1:  # All elements in the group share the same color
                consistent_groups += 1

        return consistent_groups / total_groups if total_groups > 0 else 1.0


    def check_size_proportionality(self,cluster_data):
        """
        Evaluates the proportionality of element sizes within the cluster.
        """
        sizes = cluster_data['width'] * cluster_data['height']
        size_std_dev = np.std(sizes)
        return 1 / (1 + size_std_dev)  # Lower std_dev means higher proportionality

    # Update the alignment consistency function if not already defined
    def calculate_alignment_consistency(self,group):
        """
        Measures how well elements are aligned either horizontally or vertically.
        """
        x_positions = group['position.x'].values
        y_positions = group['position.y'].values

        # Variance for alignment
        horizontal_alignment = np.var(x_positions)
        vertical_alignment = np.var(y_positions)

        # Consistency is inversely proportional to variance
        alignment_consistency = 1 / (1 + horizontal_alignment + vertical_alignment)
        return alignment_consistency
