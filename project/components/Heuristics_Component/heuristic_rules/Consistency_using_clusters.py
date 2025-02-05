import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

from components.Heuristics_Component.heuristic_rules.heuristic import HeuristicInterface

class ClusteringConsistency(HeuristicInterface):
    def __init__(self, dbscan_dataset):
        self.dbscan_dataset = dbscan_dataset  

    # def calculate_alignment_consistency(self):
    #     """Measure alignment consistency within each cluster."""
    #     cluster_scores = {}
    #     for cluster in self.df['Cluster'].unique():
    #         cluster_df = self.df[self.df['Cluster'] == cluster]
    #         horizontal_align = cluster_df['position.y'].std()  # Lower std = better alignment
    #         vertical_align = cluster_df['position.x'].std()
    #         cluster_scores[cluster] = {"horizontal": horizontal_align, "vertical": vertical_align}
    #     return cluster_scores
    def calculate_alignment_consistency(self):
        """Measure alignment consistency within each cluster."""
        required_columns = {'Cluster', 'position.x', 'position.y'}
        missing_columns = required_columns - set(self.df.columns)

        if missing_columns:
            raise KeyError(f"Missing required columns: {missing_columns}")

        cluster_scores = {}
        for cluster in self.df['Cluster'].unique():
            cluster_df = self.df[self.df['Cluster'] == cluster]
            horizontal_align = cluster_df['position.y'].std()  # Lower std = better alignment
            vertical_align = cluster_df['position.x'].std()
            cluster_scores[cluster] = {"horizontal": horizontal_align, "vertical": vertical_align}
        return cluster_scores

    def calculate_size_consistency(self):
        """Measure size consistency (width & height variations) within each cluster."""
        cluster_scores = {}
        for cluster in self.df['Cluster'].unique():
            cluster_df = self.df[self.df['Cluster'] == cluster]
            size_std = cluster_df[['width', 'height']].std()
            cluster_scores[cluster] = size_std.to_dict()
        return cluster_scores

    def calculate_spacing_consistency(self):
        """Measure spacing consistency between elements within a cluster."""
        cluster_scores = {}
        for cluster in self.df['Cluster'].unique():
            cluster_df = self.df[self.df['Cluster'] == cluster]
            
            if len(cluster_df) < 2:
                cluster_scores[cluster] = {"spacing_std": 0}  # Single-element clusters have no spacing
            
            else:
                # Compute pairwise distances in both x (horizontal) and y (vertical) directions
                x_distances = np.abs(np.diff(np.sort(cluster_df['position.x'].values)))
                y_distances = np.abs(np.diff(np.sort(cluster_df['position.y'].values)))
                
                # Standard deviation of spacing (higher std means inconsistent spacing)
                spacing_std = np.std(np.concatenate([x_distances, y_distances]))
                cluster_scores[cluster] = {"spacing_std": spacing_std}

        return cluster_scores

    def calculate_color_consistency(self):
        """Measure color consistency within each cluster."""
        cluster_scores = {}
        color_columns = [col for col in self.df.columns if col.startswith('color_')]
        
        for cluster in self.df['Cluster'].unique():
            cluster_df = self.df[self.df['Cluster'] == cluster]
            color_std = cluster_df[color_columns].std()
            cluster_scores[cluster] = color_std.to_dict()
        
        return cluster_scores
    # def generate_consistency_report(self):
    #     report = {}

    #     # Check if each feature exists in the dataset before applying rules
    #     if 'color' in self.dbscan_dataset.columns:
    #         report['color_consistency'] = self.check_color_consistency()
    #     if 'position' in self.dbscan_dataset.columns:
    #         report['position_consistency'] = self.check_position_consistency()
    #     if 'size' in self.dbscan_dataset.columns:
    #         report['size_consistency'] = self.check_size_consistency()
    #     if 'screen_size' in self.dbscan_dataset.columns:
    #         report['screen_size_consistency'] = self.check_screen_size_consistency()

    #     return report
    # def generate_consistency_report(self):
    #     """Generate a full report of cluster consistency."""
    #     return {
    #         "Alignment Consistency": self.calculate_alignment_consistency(),
    #         "Size Consistency": self.calculate_size_consistency(),
    #         "Spacing Consistency": self.calculate_spacing_consistency(),
    #         "Color Consistency": self.calculate_color_consistency(),
    #     }
    def generate_consistency_report(self):
        report = {}

        # Color Consistency
        if 'color' in self.dbscan_dataset.columns:
            color_consistency = self.calculate_color_consistency()
            report['color_consistency'] = self.analyze_consistency(color_consistency, feature="Color")

        # Position Consistency
        if 'position' in self.dbscan_dataset.columns:
            alignment_consistency = self.calculate_alignment_consistency()
            report['position_consistency'] = self.analyze_consistency(alignment_consistency, feature="Position")

        # Size Consistency
        if 'size' in self.dbscan_dataset.columns:
            size_consistency = self.calculate_size_consistency()
            report['size_consistency'] = self.analyze_consistency(size_consistency, feature="Size")

        # Screen Size Consistency
        # if 'screen_size' in self.dbscan_dataset.columns:
        #     screen_size_consistency = self.check_screen_size_consistency()
        #     report['screen_size_consistency'] = self.analyze_consistency(screen_size_consistency, feature="Screen Size")

        return report

    def analyze_consistency(self, consistency_data, feature):
        """Analyze the consistency data and return a meaningful feedback message."""
        feedback = {}
        
        # Example of a threshold logic for each feature
        if feature == "Color":
            for cluster, color_std in consistency_data.items():
                # Check if color consistency is acceptable
                if color_std['color_r'] < 0.1 and color_std['color_g'] < 0.1 and color_std['color_b'] < 0.1:
                    feedback[cluster] = "Good color consistency"
                elif color_std['color_r'] < 0.5 and color_std['color_g'] < 0.5 and color_std['color_b'] < 0.5:
                    feedback[cluster] = "Average color consistency"
                else:
                    feedback[cluster] = "Poor color consistency"

        elif feature == "Position":
            for cluster, alignment in consistency_data.items():
                # Check position consistency
                if alignment['horizontal'] < 0.1 and alignment['vertical'] < 0.1:
                    feedback[cluster] = "Good position consistency"
                elif alignment['horizontal'] < 0.5 and alignment['vertical'] < 0.5:
                    feedback[cluster] = "Average position consistency"
                else:
                    feedback[cluster] = "Poor position consistency"

        elif feature == "Size":
            for cluster, size_std in consistency_data.items():
                # Check size consistency
                if size_std['width'] < 0.1 and size_std['height'] < 0.1:
                    feedback[cluster] = "Good size consistency"
                elif size_std['width'] < 0.5 and size_std['height'] < 0.5:
                    feedback[cluster] = "Average size consistency"
                else:
                    feedback[cluster] = "Poor size consistency"

        # elif feature == "Screen Size":
        #     for cluster, screen_size_std in consistency_data.items():
        #         # Check screen size consistency
        #         if screen_size_std < 0.1:
        #             feedback[cluster] = "Good screen size consistency"
        #         elif screen_size_std < 0.5:
        #             feedback[cluster] = "Average screen size consistency"
        #         else:
        #             feedback[cluster] = "Poor screen size consistency"

        return feedback

    def detect_inconsistent_clusters(self, spacing_threshold=0.2):
        """Identify clusters with high inconsistency based on spacing variations."""
        cluster_report = self.generate_consistency_report()
        inconsistent_clusters = []

        for cluster, metrics in cluster_report["Spacing Consistency"].items():
            if metrics['spacing_std'] > spacing_threshold:
                inconsistent_clusters.append(cluster)

        return inconsistent_clusters

    def plot_alignment_consistency(self):
        """Visualize alignment consistency across clusters."""
        alignment_scores = self.calculate_alignment_consistency()
        clusters = list(alignment_scores.keys())
        horizontal_values = [v['horizontal'] for v in alignment_scores.values()]
        vertical_values = [v['vertical'] for v in alignment_scores.values()]

        plt.figure(figsize=(8,4))
        plt.bar(clusters, horizontal_values, alpha=0.5, label="Horizontal Alignment")
        plt.bar(clusters, vertical_values, alpha=0.5, label="Vertical Alignment")
        plt.xlabel("Clusters")
        plt.ylabel("Alignment Standard Deviation")
        plt.legend()
        plt.title("Alignment Consistency Per Cluster")
        plt.show()
    def evaluate_rule(self, data):
        """Implement a rule evaluation logic (dummy example below)."""
        return self.generate_consistency_report()