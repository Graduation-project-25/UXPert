from database.base_repository import BaseRepository

class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")
    

    def save_suggested_features(self, feature_data):
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
    def update_element_value(self, design_name, frame_name, element_id, field_name, new_value):
        try:
            filter_query = {
                "design_name": design_name,
                "frames.frame_name": frame_name,
                "frames.elements.id": element_id  # Ensure the element exists
            }

            update_query = {
                "$set": { f"frames.$[frame].elements.$[element].{field_name}": new_value }
            }
                # { "arrayFilters": [ { "frame.id": 102 }, { "element.id": 204 } ] }
#

            array_filters = [{ "frame.frame_name": frame_name }, { "element.id": element_id }]
            print("**********************************************************")
            print("Filter Query:", filter_query)
            print("Update Query:", update_query)
            print("Array Filters:", array_filters)
            print("**********************************************************")


            update_result = self.update_many_element(
                filter_query,
                update_query,
                array_filters=array_filters
            )

            return update_result

        except Exception as e:
            print(f"Error updating element: {e}")
            return None
