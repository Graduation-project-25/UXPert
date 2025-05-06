import datetime
import pymongo
from database.base_repository import BaseRepository
from bson.objectid import ObjectId
from bson.errors import InvalidId
class SuggestionsRepository(BaseRepository):
    def __init__(self):
            super().__init__("suggestions")

    def save_original_image_id(self, feature_data):
        # Get frame_id from feature_data or generate new ObjectId if not provided
        frame_id = feature_data.get("frame_id", str(ObjectId()))
        
        # Get the actual image data from feature_data
        image_data = feature_data.get("image64_string")
        if not image_data:
            raise ValueError("No image data found in feature_data")
        
        # Check if document with this frame_id already exists
        existing_doc = self.find_one({
            "design_name": feature_data["design_name"],
            "user_name": feature_data.get("user_name", "Unknown User"),
            "images.id": frame_id
        })
        
        # Prepare complete image entry
        image_entry = {
            "id": frame_id,
            "original_image": image_data,  # Store the actual image data
            "timestamp": datetime.datetime.utcnow(),
            "frame_data": {  # Store additional frame reference
                "page_name": feature_data.get("page_name"),
                "frame_name": feature_data.get("frame_name")
            }
        }
        
        # Upsert operation
        result = self.update(
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
                    "images": image_entry
                }
            },
            upsert=True
        )
        
        # Get the document ID (new or existing)
        doc = self.find_one({
            "design_name": feature_data["design_name"],
            "user_name": feature_data.get("user_name", "Unknown User")
        })
        
        return str(doc["_id"]) if doc else None