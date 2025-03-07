from database.base_repository import BaseRepository

class FigmaFeaturesRepository(BaseRepository):
    def __init__(self):
        super().__init__("features")  

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
            self.update(
                {"design_name": feature_data["design_name"]},
                {"$push": {"frames": feature_data}},
                upsert=True
            )

        return update_result
    
    def get_all_designs(self):
        """Retrieve all designs from the database."""
        return self.collection.find({})
    
    def get_saved_design(self, design_name, frame_name):
        """ Retrieve a saved design and its frame data """
        filter_query = {"design_name": design_name, "frames.frame_name": frame_name}
        projection = {"frames.$": 1}  # Return only the matching frame
        return self.find_one(filter_query, projection)
    
    def update_feedback(self, design_name, frame_name, feedback_data):
        """
        Update feedback for a specific frame in a design.
        """
        try:
            filter_query = {
                "design_name": design_name,
                "frames.frame_name": frame_name
            }

            update_query = {
                "$set": { "frames.$[frame].feedback": feedback_data }
            }

            array_filters = [{ "frame.frame_name": frame_name }]

            print("Filter Query:", filter_query)
            print("Update Query:", update_query)
            print("Array Filters:", array_filters)

            # Perform the update operation
            update_result = self.collection.update_many(
                filter_query,
                update_query,
                array_filters=array_filters
            )

            # Log the raw result of the update operation
            print("Update Result (Matched Count):", update_result.matched_count)
            print("Update Result (Modified Count):", update_result.modified_count)
            print("Update Result (Raw Result):", update_result.raw_result)

            return update_result
        except Exception as e:
            print(f"Error updating feedback: {e}")
            raise