import pymongo
from database.base_repository import BaseRepository
from bson.objectid import ObjectId
from bson.errors import InvalidId
class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")

    def save_original_image_id(self, imageDataUrl,feature_data):
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
        
        # Return the document _id for future reference
        if result.upserted_id:
            return result.upserted_id
        # If document existed, find and return its _id
        doc = self.find_one({
            "design_name": feature_data["design_name"],
            "user_name": feature_data.get("user_name", "Unknown User")
        })
        return str(doc["_id"]) if doc else None
        
    def get_image_by_document_id(self, document_id, image_id=None):
        try:
            query = {"_id": ObjectId(document_id)}
            projection = {}
            
            if image_id:
                # Get specific image by its ID
                query["images.id"] = image_id
                projection["images.$"] = 1
            
            result = self.find_one(query, projection)
            
            if not result:
                return None
            
            if image_id:
                return result["images"][0] if "images" in result else None
            return result.get("images", [])
            
        except InvalidId:
            return None

    def get_most_recent_image(self, document_id):
        """
        Get the most recent image from a specific document
        
        Args:
            document_id: The MongoDB _id of the document
            
        Returns:
            The most recent image document or None
        """
        try:
            result = self.find_one(
                {"_id": ObjectId(document_id)},
                {"images": {"$slice": -1}}
            )
            
            if result and "images" in result and len(result["images"]) > 0:
                return result["images"][0]
            return None
            
        except InvalidId:
            return None