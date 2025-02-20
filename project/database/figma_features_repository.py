from pymongo import MongoClient
from database.base_repository import BaseRepository

class FigmaFeaturesRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["features"])
    def add(self, feature_data):
        design_name = feature_data["design_name"]
        frame_data = {
            "frame_name": feature_data["frame_name"],
            "screen_size": feature_data["screen_size"],
            "elements": feature_data["elements"],
            "consistency_results": feature_data["consistency_results"],
            "error_prevention_results": feature_data["error_prevention_results"],
            "error_handling_results": feature_data["error_handling_results"],
            "minimalist_results": feature_data["minimalist_results"]
        }
        
        # Check if design exists, if yes, update by adding a new frame
        result = self.collection.update_one(
            {"design_name": design_name},  
            {"$push": {"frames": frame_data}},  
            upsert=True  # Create a new document if the design does not exist
        )

        return result