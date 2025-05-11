from database.base_repository import BaseRepository
from datetime import datetime

class FeedbackRepository(BaseRepository):
    def __init__(self):
        super().__init__("features")
    
    def get_feedback_by_hash(self, design_name, frame_name, data_hash):
        """Retrieve feedback by design name, frame name and data hash"""
        return self.collection.find_one({
            "design_name": design_name,
            "frame_name": frame_name,
            "data_hash": data_hash
        })
            
    def get_feedback(self, design_name, frame_name):
        """Retrieve feedback for a specific design frame"""
        return self.collection.find_one({
            'design_name': design_name,
            'frame_name': frame_name
        })      

    def get_user_history(self, user_name):
        """Retrieve all feedback history for a specific user"""
        return list(self.collection.find({
            'user_name': user_name
        }, {
            '_id': 0,
            'design_name': 1,
            'frame_name': 1,
            'created_at': 1,
            'error_prevention_results.ErrorPreventionScore': 1,
            'minimalist_results.Feedback': 1
        }).sort('created_at', -1).limit(20))

    def update_feedback(self, design_name, frame_name, feedback_data):
        try:
            # Add timestamp to feedback data
            feedback_data['created_at'] = datetime.utcnow()
            
            filter_query = {
                "design_name": design_name,
                "frames.frame_name": frame_name
            } 

            update_query = {
                "$set": { 
                    "frames.$[frame].feedback": feedback_data,
                    "user_name": feedback_data.get('user_name', 'Unknown User')
                }
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