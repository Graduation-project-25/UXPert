from bson.objectid import ObjectId
from bson.errors import InvalidId
from database.base_repository import BaseRepository

class FigmaFeaturesRepository(BaseRepository):
    def __init__(self):
        super().__init__("features")
    def get_frame_data(self, frame_id):
        """Get specific frame data by frame ID"""
        return self.collection.find_one(
            {"frames.id": frame_id},
            {"frames.$": 1}  # Projection to get only the matching frame
        )          

    def update_or_insert_frame(self, feature_data):
        """
        Update an existing frame if it exists, otherwise insert a new frame.
        """
        frame_id = feature_data.get("frame_id", str(ObjectId()))

        # Check for existing frame to avoid duplicates
        existing_frame = self.find_one({
            "design_name": feature_data["design_name"],
            "frames.frame_id": feature_data["frame_id"],
            "frames.frame_name": feature_data["frame_name"]
        })

        # If frame exists, update it
        if existing_frame and any(frame.get("frame_name") == feature_data["frame_name"] for frame in existing_frame.get("frames", [])):
            print(f"Frame '{feature_data['frame_name']}' found, updating...")
            filter_query = {
                "design_name": feature_data["design_name"],
                "user_name": feature_data["user_name"],
                "frames.frame_id": frame_id
            }
            update_query = {
                "$set": {
                    "frames.$[elem].screen_size": feature_data["screen_size"],
                    "frames.$[elem].elements": feature_data["elements"],
                    "frames.$[elem].image64_string": feature_data["image64_string"]  # Move inside array element
                }
            }
            array_filters = [{"elem.frame_id": frame_id}]
            update_result = self.update(filter_query, update_query, array_filters=array_filters)
        else:
            # If no existing frame, insert a new one
            print(f"Frame '{feature_data['frame_name']}' not found, inserting...")
            feature_data["frame_id"] = frame_id  # Ensure frame_id is part of the inserted data
            update_result = self.update(
                {"design_name": feature_data["design_name"]},
                {"$push": {"frames": feature_data}},
                upsert=True
            )

        return update_result

    def get_all_designs(self):
        """Retrieve all designs from the database."""
        return self.find_all()
    
    def get_saved_design(self, design_name, frame_name):
        """ Retrieve a saved design and its frame data """
        filter_query = {"design_name": design_name, "frames.frame_name": frame_name}
        projection = {"frames.$": 1}  # Return only the matching frame
        return self.find_one(filter_query, projection)
    
    def get_image_by_frame_id(self, design_name, frame_id):
        """Get image from a specific frame in the features collection"""
        result = self.find_one(
            {
                "design_name": design_name,
                "frames.frame_id": frame_id
            },
            {
                "frames.$": 1  # Project only the matching frame
            }
        )
        
        if result and "frames" in result and len(result["frames"]) >= 0:
            frame = result["frames"][0]
            return {
                frame.get("image64_string")
            }
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