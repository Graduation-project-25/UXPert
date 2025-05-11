import datetime
from database.base_repository import BaseRepository
from bson.objectid import ObjectId

class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")

    def save_original_image_id(self,feature_data):
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
        
    def save_modified_image(self, feature_data, modified_image_data, image_hash=None):
        # print(f"Saving modified image for frame {feature_data.get("frame_id")}")
        try:
            # First ensure the document exists
            self.collection.update_one(
                {
                    "design_name": feature_data["design_name"],
                    "user_name": feature_data.get("user_name", "Unknown User")
                },
                {
                    "$setOnInsert": {
                        "design_name": feature_data["design_name"],
                        "user_name": feature_data.get("user_name", "Unknown User"),
                        "created_at": datetime.datetime.utcnow()
                    }
                },
                upsert=True
            )

            update_data = {
                "images.$.modified_image": modified_image_data,
                "images.$.modified_at": datetime.datetime.utcnow()
            }
            
            if image_hash:
                update_data["images.$.image_hash"] = image_hash

            # Then update the specific image entry
            result = self.collection.update_one(
                {
                    "design_name": feature_data["design_name"],
                    "user_name": feature_data.get("user_name", "Unknown User"),
                    "images.id": feature_data.get("frame_id")
                },
                {
                    "$set": update_data
                }
            )

            # If no matching image was found, push a new one
            if result.matched_count == 0:
                new_image_data = {
                    "id": feature_data.get("frame_id"),
                    "modified_image": modified_image_data,
                    "modified_at": datetime.datetime.utcnow()
                }
                
                if image_hash:
                    new_image_data["image_hash"] = image_hash
                    
                self.collection.update_one(
                    {
                        "design_name": feature_data["design_name"],
                        "user_name": feature_data.get("user_name", "Unknown User")
                    },
                    {
                        "$push": {
                            "images": new_image_data
                        }
                    }
                )
            print("Image saved successfully")
            return True
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return False

    def save_text_suggestions(self, feature_data, suggestions_text):
        """Save text suggestions for a frame"""
        try:
            result = self.collection.update_one(
                {
                    "design_name": feature_data["design_name"],
                    "user_name": feature_data.get("user_name", "Unknown User"),
                    "images.id": feature_data.get("frame_id")
                },
                {
                    "$set": {
                        "images.$.suggestions_text": suggestions_text,
                        "images.$.suggestions_updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error saving suggestions: {str(e)}")
            return False
        
    def get_suggestions_for_frame(self, design_name, frame_id):
            """Get saved suggestions for a frame"""
            document = self.collection.find_one(
                {
                    "design_name": design_name,
                    "images.id": frame_id
                },
                {
                    "images.$": 1
                }
            )
            
            if document and "images" in document and len(document["images"]) > 0:
                return document["images"][0].get("suggestions_text")
            return None

    def get_image_hash_for_frame(self, design_name, frame_id):
        """Get the stored image hash for a frame"""
        document = self.collection.find_one(
            {
                "design_name": design_name,
                "images.id": frame_id
            },
            {
                "images.$": 1
            }
        )
        
        if document and "images" in document and len(document["images"]) > 0:
            return document["images"][0].get("image_hash")
        return None

    def get_modified_image(self, design_name, frame_id):
        document = self.collection.find_one({
            "design_name": design_name,
            "images.id": frame_id  
        })
        
        if document:
            # Find the specific image in the array
            for img in document.get("images", []):
                if img.get("id") == frame_id and "modified_image" in img:
                    modified_image = img["modified_image"]
                    # Ensure we return a proper data URL
                    if not modified_image.startswith('data:image'):
                        return f"data:image/png;base64,{modified_image}"
                    return modified_image
        return None
    
    def get_images_by_design(self, design_name, user_name="Unknown User"):
        """Get all images for a design"""
        result = self.find_one(
            {"design_name": design_name, "user_name": user_name},
            {"images": 1}
        )
        return result.get("images", []) if result else []
        
    def update_textual_suggestion(self, feature_data, image_hash):
        self.update_one(
                {
                    "design_name": feature_data["design_name"],
                    "user_name": feature_data.get("user_name", "Unknown User"),
                    "images.id": feature_data.get("frame_id")
                },
                {
                    "$set": {
                        "images.$.image_hash": image_hash
                    }
                }
            )