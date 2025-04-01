from PIL import Image, ImageDraw
from database.base_repository import BaseRepository

class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")
    

    def save_suggested_features(self, feature_data):
        filter_query = {
            "design_name": feature_data["design_name"],
            # "user_name": feature_data["user_name"],
            "frames.frame_name": feature_data["frame_name"]
        }
 
        update_query = {
            "$set": {
                "frames.$.screen_size": feature_data["screen_size"],
                "frames.$.elements": feature_data["elements"]
            }
        } 

        # Try to update the existing frame
        update_result = self.update(filter_query, update_query)

        if update_result.matched_count == 0:
            # If no existing frame was found, insert a new frame
            self.update(
                {"design_name": feature_data["design_name"]},
                {"$push": {"frames": feature_data}},
                upsert=True
            )

        return update_result
    def update_element_value(self, design_name, frame_name, element_id, field_name, new_value):
        try:
            filter_query = {
                "design_name": design_name,
                "frames.frame_name": frame_name,
                "frames.elements.id": element_id  # Ensure the element exists
            }

            update_query = {
                "$set": { f"frames.$[frame].elements.$[element].{field_name}": new_value }
            }

            array_filters = [{ "frame.frame_name": frame_name }, { "element.id": element_id }]
            update_result = self.update_many_element(
                filter_query,
                update_query,
                array_filters=array_filters
            )

            return update_result

        except Exception as e:
            print(f"Error updating element: {e}")
            return None

    def get_image(self):
        # Fetch JSON data
        ui_data = self.find_one({"design_name": "simple test design"})
        print("UI DATA")
        print(ui_data)
        # Extract frame details
        frame = ui_data["frames"][0]  # Assuming single frame for simplicity
        frame_width, frame_height = frame["design_name"], frame["user_name"]

        # Create a blank canvas (white background)
        image = Image.new("RGB", (frame_width, frame_height), "white")
        draw = ImageDraw.Draw(image)

        # Draw elements
        for element in frame["elements"]:
            x, y = element["position"]["x"], element["position"]["y"]
            w, h = element["width"], element["height"]
            color = tuple(element["color"])  # Convert list to tuple (R, G, B)

            draw.rectangle([x, y, x + w, y + h], fill=color)

        # Save the image
        image.save("output_ui.png")
        image.show()  # Open the image

        print("Image saved as output_ui.png")
