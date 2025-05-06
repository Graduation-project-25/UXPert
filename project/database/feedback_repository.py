from database.base_repository import BaseRepository
from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any

class FeedbackRepository(BaseRepository):
    def __init__(self):
        super().__init__("features")  # Initialize with your collection name
    
    def get_feedback(self, design_name: str, frame_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve feedback for a specific design frame
        
        Args:
            design_name: Name of the design
            frame_name: Name of the frame within the design
            
        Returns:
            The feedback document if found, None otherwise
        """
        try:
            query = {
                "design_name": design_name,
                "frames.frame_name": frame_name
            }
            
            projection = {
                "frames.$": 1,  # Return only the matching frame element
                "design_name": 1,
                "user_name": 1,
                "page_name": 1
            }
            
            document = self.collection.find_one(query, projection)
            
            if document and 'frames' in document and len(document['frames']) > 0:
                frame_data = document['frames'][0]
                return {
                    "design_name": document.get("design_name"),
                    "user_name": document.get("user_name"),
                    "page_name": document.get("page_name"),
                    "frame_name": frame_data.get("frame_name"),
                    "frame_id": frame_data.get("frame_id"),
                    "feedback": frame_data.get("feedback", {}),
                    "last_updated": frame_data.get("last_updated")
                }
            return None
            
        except Exception as e:
            print(f"Error getting feedback: {e}")
            raise

    def update_feedback(self, design_name: str, frame_name: str, feedback_data: Dict[str, Any]):
        """
        Update or insert feedback for a specific design frame
        
        Args:
            design_name: Name of the design
            frame_name: Name of the frame within the design
            feedback_data: Dictionary containing feedback results
            
        Returns:
            UpdateResult object
        """
        try:
            filter_query = {
                "design_name": design_name,
                "frames.frame_name": frame_name
            } 

            update_query = {
                "$set": { 
                    "frames.$[frame].feedback": feedback_data,
                    "frames.$[frame].last_updated": datetime.now(),
                    "last_updated": datetime.now()
                }
            }

            array_filters = [{ "frame.frame_name": frame_name }]

            print("Updating feedback with:")
            print("Filter Query:", filter_query)
            print("Update Query:", update_query)
            print("Array Filters:", array_filters)

            update_result = self.update_many_element(
                filter_query,
                update_query,
                array_filters=array_filters
            )

            # If no existing frame was found, insert a new one
            if update_result.matched_count == 0:
                print("No existing frame found, inserting new frame with feedback")
                return self._insert_new_frame_with_feedback(
                    design_name, 
                    frame_name, 
                    feedback_data
                )

            print("Feedback update successful:")
            print("Matched Count:", update_result.matched_count)
            print("Modified Count:", update_result.modified_count)
            
            return update_result
            
        except Exception as e:
            print(f"Error updating feedback: {e}")
            raise

    def _insert_new_frame_with_feedback(self, design_name: str, frame_name: str, feedback_data: Dict[str, Any]):
        """
        Insert a new frame with feedback data when no existing frame is found
        
        Args:
            design_name: Name of the design
            frame_name: Name of the frame to create
            feedback_data: Feedback data to include
            
        Returns:
            UpdateResult object
        """
        try:
            update_query = {
                "$push": {
                    "frames": {
                        "frame_name": frame_name,
                        "feedback": feedback_data,
                        "last_updated": datetime.now()
                    }
                },
                "$set": {
                    "last_updated": datetime.now()
                }
            }
            
            return self.collection.update_one(
                {"design_name": design_name},
                update_query,
                upsert=True
            )
        except Exception as e:
            print(f"Error inserting new frame: {e}")
            raise

    def delete_feedback(self, design_name: str, frame_name: str):
        """
        Delete feedback for a specific design frame
        
        Args:
            design_name: Name of the design
            frame_name: Name of the frame within the design
            
        Returns:
            DeleteResult object
        """
        try:
            return self.collection.update_one(
                {"design_name": design_name},
                {"$pull": {"frames": {"frame_name": frame_name}}}
            )
        except Exception as e:
            print(f"Error deleting feedback: {e}")
            raise

    def get_all_feedback_for_design(self, design_name: str):
        """
        Get all feedback for a specific design
        
        Args:
            design_name: Name of the design
            
        Returns:
            List of feedback documents
        """
        try:
            return list(self.collection.find(
                {"design_name": design_name},
                {"frames.feedback": 1, "frames.frame_name": 1}
            ))
        except Exception as e:
            print(f"Error getting all feedback: {e}")
            raise