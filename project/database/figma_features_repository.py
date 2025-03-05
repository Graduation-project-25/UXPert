from database.base_repository import BaseRepository

class FigmaFeaturesRepository(BaseRepository):
    def __init__(self):
        super().__init__("features")  # Assuming "features" is the collection name

    def update_or_insert_frame(self, feature_data):
        """
        Update an existing frame if it exists, otherwise insert a new frame.
        """ 
        filter_query = {
            "design_name": feature_data["design_name"],
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
            self.upsert(
                {"design_name": feature_data["design_name"]},
                {"$push": {"frames": feature_data}},
                upsert=True
            )

        return update_result
