import numpy as np
import pandas as pd
import cv2
from collections import Counter
from skimage.color import rgb2lab
from scipy.spatial.distance import euclidean
from sklearn.cluster import KMeans
from components.Heuristics_Component.heuristic import HeuristicInterface


class Consistency(HeuristicInterface):
    
    def prepare_data_for_evaluation(self, extracted_features=None):
        if extracted_features is None:
            raise ValueError("extracted_features must be provided")

        data = {
            'width': extracted_features.get('width', []),
            'height': extracted_features.get('height', []),
            'color_r': extracted_features.get('color_r', []),
            'color_g': extracted_features.get('color_g', []),
            'color_b': extracted_features.get('color_b', []),
            'position.x': extracted_features.get('position_x', []),
            'position.y': extracted_features.get('position_y', [])
        }

        df = pd.DataFrame(data)
        df.fillna(method='ffill', inplace=True)  # Forward fill missing values
        return df

#  third try : 
    def calculate_alignment_consistency(self, cluster_data, threshold=5):
        """
        Measures how well elements are aligned either horizontally or vertically using clustering techniques.
        A threshold defines how close elements should be to count as aligned.
        """
        x_positions = cluster_data['position.x'].values
        y_positions = cluster_data['position.y'].values

        # Count occurrences of x and y positions within a small threshold
        x_counts = Counter([round(x / threshold) * threshold for x in x_positions])
        y_counts = Counter([round(y / threshold) * threshold for y in y_positions])

        # Find the most common positions and count how many elements are close to them
        dominant_x = max(x_counts.values()) / len(x_positions)
        dominant_y = max(y_counts.values()) / len(y_positions)

        # Compute alignment score based on how many elements fall into the dominant clusters
        alignment_score = (dominant_x + dominant_y) / 2  # Averaging horizontal and vertical alignment scores

        return alignment_score


    @staticmethod
    def rgb_to_lab(rgb_color):
        """Convert an RGB color to LAB format for better color similarity detection."""
        if not isinstance(rgb_color, (list, tuple, np.ndarray)) or len(rgb_color) != 3:
            raise ValueError(f"Invalid RGB color format: {rgb_color}")

        # Convert color to 0-255 scale
        rgb_color = np.array([[np.array(rgb_color) * 255]], dtype=np.uint8)
        lab_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2LAB)
        return lab_color[0][0]

    @staticmethod
    def color_distance(lab1, lab2):
        """Calculate Euclidean distance between two LAB colors."""
        return np.linalg.norm(np.array(lab1) - np.array(lab2))

    @staticmethod
    def prepare_data_for_evaluation(extracted_features):
        """Prepare extracted features into a DataFrame."""
        required_keys = ['width', 'height', 'color_r', 'color_g', 'color_b', 'position_x', 'position_y']
        for key in required_keys:
            if key not in extracted_features:
                extracted_features[key] = []  # Ensure all required keys exist

        data = {
            'width': extracted_features.get('width', []),
            'height': extracted_features.get('height', []),
            'color_r': extracted_features.get('color_r', []),
            'color_g': extracted_features.get('color_g', []),
            'color_b': extracted_features.get('color_b', []),
            'position.x': extracted_features.get('position_x', []),
            'position.y': extracted_features.get('position_y', [])
        }

        df = pd.DataFrame(data)
        df = df.ffill()  # Forward fill missing values
        return df

    def check_color_consistency(self, cluster_data, shade_threshold=20, overall_variation_threshold=5):
        """
        Evaluates color consistency:
        - Groups elements by size.
        - Checks if most elements in each size group share the same color.
        - Detects too many color variations in the overall design.
        - Uses KMeans to determine dominant colors.
        """
        if isinstance(cluster_data, Consistency):
            cluster_data = cluster_data.prepare_data_for_evaluation(cluster_data)

        if not isinstance(cluster_data, pd.DataFrame):
            raise ValueError("cluster_data must be a Pandas DataFrame")

        # Convert RGB colors to LAB for better comparison
        lab_values = cluster_data.apply(
            lambda row: self.rgb_to_lab([row['color_r'], row['color_g'], row['color_b']]), axis=1
        )

        # Convert LAB values into separate DataFrame columns
        lab_df = pd.DataFrame(lab_values.tolist(), columns=['lab_l', 'lab_a', 'lab_b'])

        # Merge LAB values into cluster_data
        cluster_data = pd.concat([cluster_data, lab_df], axis=1)

        # Convert colors to proper scale (0-255)
        cluster_data[['color_r', 'color_g', 'color_b']] = (cluster_data[['color_r', 'color_g', 'color_b']] * 255).astype(int)

        # Step 1: Detect overall color variation using KMeans clustering
        color_data = cluster_data[['color_r', 'color_g', 'color_b']].values

        # Prevent errors if fewer colors exist
        num_colors = min(5, len(color_data))  
        kmeans = KMeans(n_clusters=num_colors, n_init=10, random_state=42)
        kmeans.fit(color_data)
        unique_design_colors = kmeans.cluster_centers_

        # Step 2: Group by size
        cluster_data['size'] = cluster_data['width'] * cluster_data['height']
        size_groups = cluster_data.groupby('size')

        color_consistency_score = 0
        num_groups = len(size_groups)

        for _, group in size_groups:
            # Get all LAB colors in the group
            lab_colors = group[['lab_l', 'lab_a', 'lab_b']].values

            # Find dominant colors (grouping shades together)
            dominant_colors = []
            for lab in lab_colors:
                matched = False
                for dom in dominant_colors:
                    if self.color_distance(lab, dom) < shade_threshold:
                        matched = True
                        break
                if not matched:
                    dominant_colors.append(lab)

            # Adjust scoring based on number of dominant colors
            if len(dominant_colors) == 1:
                color_consistency_score += 1
            elif len(dominant_colors) <= 3:
                color_consistency_score += 0.5  # Small variation
            else:
                color_consistency_score += 0.2  # High variation

        # Step 3: Apply color variation penalty
        color_variation_penalty = max(0, (len(unique_design_colors) - overall_variation_threshold) * 5)

        # Step 4: Prevent division by zero
        if num_groups == 0:
            final_color_consistency_score = 0
        else:
            final_color_consistency_score = max(0, ((color_consistency_score / num_groups) * 100) - color_variation_penalty)

        return round(final_color_consistency_score, 2)
    def check_size_proportionality(self, cluster_data, threshold=0.3):
        """
        Evaluates size proportionality by measuring how well elements fit into common size groups.
        """
        sizes = cluster_data['width'] * cluster_data['height']
        mean_size = np.mean(sizes)

        # Compute how many elements are within a reasonable range of mean size
        size_ratios = sizes / mean_size
        proportional_elements = np.sum((1 - threshold) <= size_ratios) / len(sizes)

        return proportional_elements
    def evaluate_rule(self, cluster_data):
        """
        Evaluates the consistency of a cluster based on:
        1. Color similarity among similar-sized elements.
        2. Horizontal and vertical alignment.
        3. Proportional element sizes.
        """
        if not isinstance(cluster_data, pd.DataFrame):
            raise TypeError("cluster_data must be a pandas DataFrame")

        required_columns = ['width', 'height', 'color_r', 'color_g', 'color_b', 'position.x', 'position.y']
        if not all(col in cluster_data.columns for col in required_columns):
            raise ValueError("Missing necessary columns")

        # Ensure that functions return numeric values
        color_score = self.check_color_consistency(cluster_data)
        alignment_score = self.calculate_alignment_consistency(cluster_data) if hasattr(self, 'calculate_alignment_consistency') else 1
        size_score = self.check_size_proportionality(cluster_data) if hasattr(self, 'check_size_proportionality') else 1

        # Compute final consistency score with adaptive weights
        total_score = (0.4 * color_score + 0.3 * alignment_score + 0.3 * size_score)

        feedback = {
            "ColorConsistency": round(color_score, 2),
            "AlignmentConsistency": round(alignment_score * 100, 2),
            "SizeProportionality": round(size_score * 100, 2),
            "TotalConsistency": round(total_score * 100, 2),
            "Feedback": {
                "Color": "Colors are perceptually consistent" if color_score > 0.9 else "Color variation detected.",
                "Alignment": "Elements are well-aligned" if alignment_score > 0.8 else "Alignment issues detected.",
                "Size": "Elements follow proportional sizes" if size_score > 0.8 else "Size inconsistency detected."
            }
        }

        return feedback



    # def check_color_consistency(self, cluster_data):
    #     """
    #     Check for color consistency between similar-sized elements.
    #     Returns a score based on the degree of consistency.
    #     """
    #     # Group elements by size (width and height)
    #     cluster_data['size'] = cluster_data['width'] * cluster_data['height']
    #     similar_size_groups = cluster_data.groupby('size')
        
    #     color_consistency_score = 0
    #     num_groups = len(similar_size_groups)
        
    #     for _, group in similar_size_groups:
    #         unique_colors = group[['color_r', 'color_g', 'color_b']].drop_duplicates()
    #         if len(unique_colors) == 1:
    #             color_consistency_score += 1  # Consistent color for all elements in this size group
    #         else:
    #             color_consistency_score += 0.5  # Partially consistent or inconsistent colors
        
    #     return color_consistency_score / num_groups if num_groups > 0 else 0

    # def calculate_alignment_consistency(self, cluster_data):
    #     """
    #     Measures how well elements are aligned either horizontally or vertically.
    #     You can adjust weights for horizontal and vertical alignment.
    #     """
    #     x_positions = cluster_data['position.x'].values
    #     y_positions = cluster_data['position.y'].values

    #     # Calculate the variance in x and y positions
    #     horizontal_alignment = np.var(x_positions)
    #     vertical_alignment = np.var(y_positions)

    #     # Adjust horizontal and vertical alignment weight
    #     horizontal_weight = 0.6  # Adjust this based on importance in your design
    #     vertical_weight = 0.4    # Adjust this based on importance in your design

    #     # Weighted alignment score
    #     alignment_score = 1 / (1 + (horizontal_weight * horizontal_alignment + vertical_weight * vertical_alignment))

    #     return alignment_score

    # def check_size_proportionality(self, cluster_data):
    #     """
    #     Evaluates the proportionality of element sizes within the cluster.
    #     Adds a threshold to define the acceptable range of size variation.
    #     """
    #     # Calculate the area of each element (width * height)
    #     sizes = cluster_data['width'] * cluster_data['height']
    #     size_std_dev = np.std(sizes)  # Standard deviation to measure variation

    #     # Define a threshold for acceptable size variation
    #     size_threshold = 50  # Example threshold; tweak it according to your needs
    #     return max(0, 1 - size_std_dev / size_threshold)  # Normalize based on the threshold

    # def evaluate_rule(self, cluster_data):
    #     """
    #     Evaluates the consistency of a cluster based on:
    #     1. Similar elements with the same size having the same color.
    #     2. Alignment (horizontal/vertical).
    #     3. Proportional sizes of elements.
    #     """
    #     # Ensure `cluster_data` is in a proper DataFrame format
    #     if not isinstance(cluster_data, pd.DataFrame):
    #         raise TypeError("cluster_data must be a pandas DataFrame")
        
    #     # Check for the necessary columns
    #     required_columns = ['width', 'height', 'color_r', 'color_g', 'color_b', 'position.x', 'position.y']
    #     missing_columns = [col for col in required_columns if col not in cluster_data.columns]
    #     if missing_columns:
    #         raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

    #     # Calculate the individual scores
    #     color_consistency_score = self.check_color_consistency(cluster_data)
    #     alignment_consistency_score = self.calculate_alignment_consistency(cluster_data)
    #     size_proportionality_score = self.check_size_proportionality(cluster_data)

    #     # Combine scores with respective weights
    #     total_consistency_score = (
    #         0.4 * color_consistency_score +
    #         0.3 * alignment_consistency_score +
    #         0.3 * size_proportionality_score
    #     )

    #     # Detailed feedback
    #     feedback = {
    #         "ColorConsistency": round(color_consistency_score * 100, 2),
    #         "AlignmentConsistency": round(alignment_consistency_score * 100, 2),
    #         "SizeProportionality": round(size_proportionality_score * 100, 2),
    #         "TotalConsistency": round(total_consistency_score * 100, 2),
    #         "Feedback": {
    #             "ColorConsistency": "Colors are consistent across similar-sized elements."
    #             if color_consistency_score > 0.9 else "Colors are inconsistent for some similar-sized elements.",
    #             "AlignmentConsistency": "Elements are well-aligned horizontally and vertically."
    #             if alignment_consistency_score > 0.9 else "Alignment needs improvement.",
    #             "SizeProportionality": "The size variation is within acceptable limits."
    #             if size_proportionality_score > 0.8 else "Size proportionality is off, consider adjusting element sizes."
    #         }
    #     }

    #     return feedback


    # second try 
    # def check_color_consistency(self, cluster_data):
    #     cluster_data['size'] = cluster_data['width'] * cluster_data['height']
    #     similar_size_groups = cluster_data.groupby('size')

    #     scores = []
    #     for _, group in similar_size_groups:
    #         color_variance = np.var(group[['color_r', 'color_g', 'color_b']], axis=0).sum()
    #         scores.append(1 / (1 + color_variance))  # Normalize score (lower variance → higher score)
        
    #     return np.mean(scores) if scores else 0

    # def calculate_alignment_consistency(self, cluster_data):
    #     x_std = np.std(cluster_data['position.x'])
    #     y_std = np.std(cluster_data['position.y'])

    #     alignment_score = 1 - (x_std + y_std) / (max(x_std, y_std) + 1e-5)  # Normalize score
    #     return max(0, alignment_score)  # Ensure score is non-negative
    # def check_size_proportionality(self, cluster_data):
    #     sizes = cluster_data['width'] * cluster_data['height']
    #     size_std_dev = np.std(sizes)
        
    #     size_threshold = np.mean(sizes) * 0.2  # Dynamic threshold (20% of mean size)
    #     return max(0, 1 - size_std_dev / (size_threshold + 1e-5))
    # def evaluate_rule(self, cluster_data):
    #     if not isinstance(cluster_data, pd.DataFrame):
    #         raise TypeError("cluster_data must be a pandas DataFrame")

    #     required_columns = ['width', 'height', 'color_r', 'color_g', 'color_b', 'position.x', 'position.y']
    #     if any(col not in cluster_data.columns for col in required_columns):
    #         raise ValueError("Missing required columns in cluster_data.")

    #     # Calculate the individual scores
    #     color_score = self.check_color_consistency(cluster_data)
    #     alignment_score = self.calculate_alignment_consistency(cluster_data)
    #     size_score = self.check_size_proportionality(cluster_data)

    #     # **Use a geometric mean for better weighting**
    #     total_consistency_score = (color_score**0.4) * (alignment_score**0.3) * (size_score**0.3)

    #     # Detailed feedback
    #     feedback = {
    #         "ColorConsistency": round(color_score * 100, 2),
    #         "AlignmentConsistency": round(alignment_score * 100, 2),
    #         "SizeProportionality": round(size_score * 100, 2),
    #         "TotalConsistency": round(total_consistency_score * 100, 2),
    #         "Feedback": {
    #             "ColorConsistency": "Good color consistency." if color_score > 0.9 else "Some colors are inconsistent.",
    #             "AlignmentConsistency": "Elements are well-aligned." if alignment_score > 0.5 else "Alignment needs improvement.",
    #             "SizeProportionality": "Sizes are proportional." if size_score > 0.8 else "Size variation is high."
    #         }
    #     }

    #     return feedback


