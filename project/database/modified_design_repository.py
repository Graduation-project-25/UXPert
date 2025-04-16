# modified_designs_repository.py
from database.base_repository import BaseRepository
import os
import json
from datetime import datetime

class ModifiedDesignsRepository(BaseRepository):
    def __init__(self):
        super().__init__("modified_designs")
        
    def save_modified_design(self, original_data, modified_json):
        """
        Save both original design and modified JSON to database and file system
        Returns:
            tuple: (document_id, filename)
        """
        # Create comprehensive document structure
        document = {
            "original": {
                "design_name": original_data.get('design_name', 'Untitled'),
                "user_name": original_data.get('user_name', 'Unknown'),
                "design_json": original_data['design_json'],
                "timestamp": datetime.utcnow()
            },
            "modified": modified_json,  # This is the AI's response JSON
            "files": {
                "original_saved": False,
                "modified_saved": False
            }
        }
        
        # First save to database
        result = self.add(document)
        document_id = str(result.inserted_id)
        
        # Then save to file system
        try:
            os.makedirs("modified_designs", exist_ok=True)
            
            # Save original and modified as separate files
            original_filename = f"modified_designs/original_{document_id}.json"
            modified_filename = f"modified_designs/modified_{document_id}.json"
            
            # Save original design
            with open(original_filename, 'w') as f:
                json.dump(original_data, f, indent=2)
            
            # Save modified JSON
            with open(modified_filename, 'w') as f:
                json.dump(modified_json, f, indent=2)
            
            # Update document with file info
            self.update(
                {"_id": result.inserted_id},
                {"$set": {
                    "files": {
                        "original_saved": original_filename,
                        "modified_saved": modified_filename
                    }
                }}
            )
            
            return document_id, (original_filename, modified_filename)
            
        except Exception as e:
            print(f"Error saving to files: {e}")
            # Even if file save fails, we still have the data in DB
            return document_id, (None, None)
        
    def get_modification_by_id(self, modification_id):
        """Get a single modification by its ID"""
        return self.find_by_id(modification_id)

    def get_modifications_for_design(self, design_name):
        """Get all modifications for a specific design"""
        return list(self.collection.find(
            {"original_design_name": design_name},
            sort=[("timestamp", -1)]  # Newest first
        ))

    def get_modifications_by_user(self, user_name):
        """Get all modifications by a specific user"""
        return list(self.collection.find(
            {"original_user_name": user_name},
            sort=[("timestamp", -1)]
        ))