from database.base_repository import BaseRepository

class FeedbackRepository(BaseRepository):
    def __init__(self):
        super().__init__("features")
        
    def get_feedback(self, design_name, frame_name):
        """Retrieve feedback for a specific design frame"""
        return self.collection.find_one({
            'design_name': design_name,
            'frame_name': frame_name
        })      

    def update_feedback(self, design_name, frame_name, feedback_data):
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
            update_result = self.update_many_element(
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