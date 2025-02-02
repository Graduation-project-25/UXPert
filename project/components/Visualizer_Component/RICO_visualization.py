import os
import cv2
import json
from components.Visualizer_Component.visualizer import visualizer

class Rico_Visualization(visualizer):

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
            output_path = os.path.join(output_folder, json_files[index])

            print(f"Processing: {json_file_path}")
            ui_elements = extract_rico_ui_elements(json_file_path)

            # Save the extracted elements to the output folder
            save_ui_elements(ui_elements, output_path)

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
        
        # Include additional information for Rico dataset
        if element.get('clickable'):
            label_text += " (Clickable)"
        if element.get('enabled') is False:
            label_text += " (Disabled)"

        # Add label text to image
        cv2.putText(
            image, label_text, (x, text_y_position),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
        )
