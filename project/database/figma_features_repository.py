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
    
    def get_all_designs(self):
        """Retrieve all designs from the database."""
        return self.find_all()
    
    def get_saved_design(self, design_name, frame_name):
        """ Retrieve a saved design and its frame data """
        filter_query = {"design_name": design_name, "frames.frame_name": frame_name}
        projection = {"frames.$": 1}  # Return only the matching frame
        return self.find_one(filter_query, projection)
    