import datetime
from database.base_repository import BaseRepository
from bson.objectid import ObjectId
class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")

    def save_original_image_id(self,feature_data):
        frame_id = feature_data.get("frame_id", str(ObjectId()))  # Use frameId or generate ObjectId
        # Check if image with frame_id exists
        query = {
            "design_name": feature_data["design_name"],
            "user_name": feature_data.get("user_name", "Unknown User"),
            "images.id": frame_id
        }
        if self.find_one(query):
            return {
                "message": f"Frame with id '{frame_id}' already exists",
                "design_id": str(self.find_one(query)["_id"])
            }
        image_entry = {
            "id": frame_id,  # Use frameId or generate ObjectId
            # "original_image": imageDataUrl  
        }
        result =self.update(
            {
                "design_name": feature_data["design_name"],
                "user_name": feature_data.get("user_name", "Unknown User")
            },
            {
                "$set": {
                    "design_name": feature_data["design_name"],
                    "user_name": feature_data.get("user_name", "Unknown User"),
                },
                "$push": {
                    "images": image_entry  # Append image to images array
                }
            },
            upsert=True  # Create new document if it doesn't exist
        )
        
        # # Return the document _id for future reference
        # if result.upserted_id:
        #     return result.upserted_id
        # # If document existed, find and return its _id
        # doc = self.find_one({
        #     "design_name": feature_data["design_name"],
        #     "user_name": feature_data.get("user_name", "Unknown User")
        # })
        # return str(doc["_id"]) if doc else None

    def save_modified_image(self, design_name, user_name, frame_id, modified_image_data):
            """Save modified image for a specific frame"""
            return self.update(
                {
                    "design_name": design_name,
                    "user_name": user_name,
                    "images.id": frame_id
                },
                {
                    "$set": {
                        "images.$.modified_image": modified_image_data,
                        "images.$.modified_at": datetime.datetime.utcnow()
                    }
                }
            )
    
    def get_images_by_design(self, design_name, user_name="Unknown User"):
        """Get all images for a design"""
        result = self.find_one(
            {"design_name": design_name, "user_name": user_name},
            {"images": 1}
        )
        return result.get("images", []) if result else []
        
