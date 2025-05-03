import base64
from io import BytesIO
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

    def save_design_with_images(self, design_data):
        """
        Save design data with original and modified images
        Args:
            design_data: {
                "design_name": str,
                "user_name": str,
                "frames": [{
                    "frame_name": str,
                    "original_image": base64 str,
                    "modified_image": base64 str (optional),
                    "elements": list
                }]
            }
        """
        # Convert images to base64 if they're PIL images
        for frame in design_data.get("frames", []):
            if isinstance(frame.get("original_image"), Image.Image):
                frame["original_image"] = self.image_to_base64(frame["original_image"])
            if isinstance(frame.get("modified_image"), Image.Image):
                frame["modified_image"] = self.image_to_base64(frame["modified_image"])
        
        # Upsert the design data
        return self.update(
            {"design_name": design_data["design_name"]},
            {"$set": design_data},
            upsert=True
        )

    def get_design_images(self, design_name, frame_name):
        """
        Retrieve original and modified images for a design frame
        Returns: (original_image, modified_image) as PIL Images
        """
        design = self.find_one(
            {"design_name": design_name, "frames.frame_name": frame_name},
            {"frames.$": 1}
        )
        
        if not design or not design.get("frames"):
            return None, None
            
        frame = design["frames"][0]
        original = self.base64_to_image(frame.get("original_image")) if frame.get("original_image") else None
        modified = self.base64_to_image(frame.get("modified_image")) if frame.get("modified_image") else None
        
        return original, modified

    @staticmethod
    def image_to_base64(image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def base64_to_image(base64_str):
        """Convert base64 string to PIL Image"""
        return Image.open(BytesIO(base64.b64decode(base64_str)))