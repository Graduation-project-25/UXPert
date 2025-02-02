import os
import cv2
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt


from components.Visualizer_Component.visualizer import VisualizerInterface
from project.components.Feature_Extractor_Component.EGFE_ui_extraction import EGFE_FeatureExtraction

class EGFE_Visualization(VisualizerInterface):
    def __init__(self):
        self.egfe_ui_extraction = EGFE_FeatureExtraction()
        
    def visualize_ui_elements(self, image_folder, json_folder, output_folder, limit=50):
        """Visualizes the extracted UI elements on their corresponding images."""
        json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')][:limit]
        index = 0

        while True:
            if index >= len(json_files):
                index = 0

            json_file_path = os.path.join(json_folder, json_files[index])
            image_name = json_files[index].replace('.json', '.png')
            image_path = os.path.join(image_folder, image_name)
            # output_path = os.path.join(output_folder, json_files[index])

            print(f"Processing: {json_file_path}")
            ui_elements = self.egfe_ui_extraction.extract_ui_elements(json_file_path)

            # Save the extracted elements to the output folder
            # self.egfe_ui_extraction.save_ui_elements(ui_elements, output_path)

            # Load image and draw bounding boxes
            image = cv2.imread(image_path)
            if image is None:
                print(f"Image could not be loaded: {image_path}")
                index += 1
                continue

            for element in ui_elements:
                self.draw_bounding_box(element, image)

            # Display the image with bounding boxes
            cv2.imshow("UI Elements", image)
            key = cv2.waitKey(0)  # Wait for a key press to proceed to the next image
            if key == 27:  # Esc key to exit
                break
            index += 1

        cv2.destroyAllWindows()

    def draw_bounding_box(self, element, image):
        position = element.get('position', {'x': 0, 'y': 0})
        width = element.get('width', 0)
        height = element.get('height', 0)
        x, y = position['x'], position['y']

        # Draw bounding box around the element
        cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)

        # Add a small offset for better text placement and to prevent overlapping
        text_y_position = y - 10 if y - 10 > 0 else y + height + 20
        label_text = f"{element['type']}: {element['name']}" if element.get('name') else element['type']
        cv2.putText(
            image, label_text, (x, text_y_position),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
        )

    def scatter_plot_ui_elements(self, df):
        """Generates a scatter plot for UI elements based on position and size."""
        # plt.figure(figsize=(8, 6))

        # Scatter plot for position.x vs position.y
        plt.scatter(df['position.x'], df['position.y'], c='blue', label='Position', alpha=0.6)
        
        # Another scatter plot for width vs height
        plt.scatter(df['width'], df['height'], c='red', label='Size', alpha=0.6)

        plt.xlabel('Position X / Width')
        plt.ylabel('Position Y / Height')
        plt.title('Scatter Plot of UI Elements')
        plt.legend()
        
        # Show plot
        plt.show()


    def clustering_visualization_by_size(self, DBSCAN_dataset,clusters):
        # Plot noise points (-1)
        if -1 in clusters: 
            # Assert 'Cluster' in DBSCAN_dataset.columns, "Column 'Cluster' not found in DBSCAN_dataset"
            plt.scatter(
                DBSCAN_dataset[DBSCAN_dataset['Cluster'] == -1]['width'],
                DBSCAN_dataset[DBSCAN_dataset['Cluster'] == -1]['height'],
                s=20, color='black', label='Noise'
            )

        # Plot each cluster
        colors = ['blue', 'red', 'yellow', 'green', 'purple', 'orange', 'pink', 'brown', 'cyan']
        for cluster_id, color in zip(clusters[clusters >= 0], colors):
            cluster_data = DBSCAN_dataset[DBSCAN_dataset['Cluster'] == cluster_id]
            plt.scatter(
                cluster_data['width'], 
                cluster_data['height'], 
                s=20, color=color, label=f'Cluster {cluster_id}'
            )
        # Add plot details
        plt.title("DBSCAN Clustering Visualization")
        plt.xlabel("Width")
        plt.ylabel("Height")
        plt.legend()
        plt.show()

    def clustering_visualization_by_position(self, DBSCAN_dataset, clusters):
        # Plot noise points (-1)
        if -1 in clusters: 
            # Assert 'Cluster' in DBSCAN_dataset.columns, "Column 'Cluster' not found in DBSCAN_dataset"
            plt.scatter(
                DBSCAN_dataset[DBSCAN_dataset['Cluster'] == -1]['position.x'],
                DBSCAN_dataset[DBSCAN_dataset['Cluster'] == -1]['position.y'],
                s=20, color='black', label='Noise'
            )

        # Plot each cluster
        colors = ['blue', 'red', 'yellow', 'green', 'purple', 'orange', 'pink', 'brown', 'cyan']
        for cluster_id, color in zip(clusters[clusters >= 0], colors):
            cluster_data = DBSCAN_dataset[DBSCAN_dataset['Cluster'] == cluster_id]
            plt.scatter(
                cluster_data['position.x'], 
                cluster_data['position.y'], 
                s=20, color=color, label=f'Cluster {cluster_id}'
            )
        # Add plot details
        plt.title("DBSCAN Clustering Visualization")
        plt.xlabel("Position X") 
        plt.ylabel("Position Y")
        plt.legend()
        plt.show()

    # def ensure_consistency_score(analysis_df):
    #     # Debugging: Check the columns in the DataFrame
    #     print("Checking columns in analysis_df:", analysis_df.columns)
        
    #     if 'ConsistencyScore' not in analysis_df.columns:
    #         # Check for required metrics
    #         if 'Metric1' in analysis_df.columns and 'Metric2' in analysis_df.columns:
    #             # Example calculation of ConsistencyScore
    #             analysis_df['ConsistencyScore'] = (analysis_df['Metric1'] + analysis_df['Metric2']) / 2
    #         else:
    #             # Handle missing required metrics
    #             print("Required metrics are missing for calculating 'ConsistencyScore'.")
    #             analysis_df['ConsistencyScore'] = 0  # Default value or impute as needed
    #             print("Default 'ConsistencyScore' set to 0.")
    #     return analysis_df

    def visualize_alignment_consistency(self, cluster_data):
        plt.figure(figsize=(10, 5))
        plt.scatter(cluster_data['position.x'], cluster_data['position.y'], c='blue', label='UI Elements', alpha=0.6)

        plt.title('Alignment Consistency of UI Elements')
        plt.xlabel('Position X')
        plt.ylabel('Position Y')
        plt.axvline(x=cluster_data['position.x'].mean(), color='red', linestyle='--', label='Avg X Position')
        plt.axhline(y=cluster_data['position.y'].mean(), color='green', linestyle='--', label='Avg Y Position')
        plt.legend()
        plt.show()
        
    def visualize_color_consistency(self, cluster_data):
        """
        Visualizes color consistency based on size groups.
        Displays proportion of consistent vs inconsistent color groups.
        """
        size_groups = cluster_data.groupby(['width', 'height'])
        consistent_groups = 0
        inconsistent_groups = 0

        for _, group in size_groups:
            unique_colors = group[['color_r', 'color_g', 'color_b']].drop_duplicates().shape[0]
            if unique_colors == 1:
                consistent_groups += 1
            else:
                inconsistent_groups += 1

        labels = ['Consistent Color Groups', 'Inconsistent Color Groups']
        sizes = [consistent_groups, inconsistent_groups]

        plt.figure(figsize=(8, 6))
        plt.bar(labels, sizes, color=['green', 'red'])
        plt.title('Color Consistency in UI Elements')
        plt.ylabel('Number of Groups')
        plt.show()
    
    def visualize_size_proportionality(self, cluster_data):
        """
        Visualizes the size proportionality of UI elements in a cluster.
        This visualization uses a box plot to show the distribution of sizes.
        """
        sizes = cluster_data['width'] * cluster_data['height']  # Calculate element sizes
        plt.figure(figsize=(10, 6))
        
        plt.boxplot(sizes, vert=False)
        plt.title('Size Proportionality of UI Elements')
        plt.xlabel('Size (Width * Height)')
        plt.grid()
        plt.show()
        
