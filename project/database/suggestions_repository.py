import pymongo
from database.base_repository import BaseRepository
from bson.objectid import ObjectId

class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")

    def save_original_image(self, imageDataUrl,feature_data):
        image_entry = {
            "id": feature_data.get("frame_id", str(ObjectId())),  # Use frameId or generate ObjectId
            # "original_image": imageDataUrl  
        }
        self.update(
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
    def get_original_image(self,feature_data, image_id):
        self.find_one({
            "design_name": feature_data["design_name"],
        })




