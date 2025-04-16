# modified_designs_repository.py
from database.base_repository import BaseRepository
import os
import json
from datetime import datetime

class ModifiedDesignsRepository(BaseRepository):
    def __init__(self):
        super().__init__("modified_designs")
        
    def save_modified_design(self, original_data, modifications):
        """Save modified design to database and file system"""
        # Create document structure
        document = {
            "original_design_name": original_data.get('design_name', 'Untitled'),
            "original_user_name": original_data.get('user_name', 'Unknown'),
            "original_design_json": original_data['design_json'],
            "modifications": modifications,
            "timestamp": datetime.utcnow(),
            "saved_files": []
        }
        
        # Save to database
        result = self.add(document)
        document_id = str(result.inserted_id)
        
        # Save to file system
        try:
            os.makedirs("modified_designs", exist_ok=True)
            filename = f"modified_designs/modified_{document_id}.json"
            with open(filename, 'w') as f:
                json.dump({
                    "original": original_data,
                    "modifications": modifications
                }, f, indent=2)
            
            # Update document with file info
            self.update(
                {"_id": result.inserted_id},
                {"$push": {"saved_files": filename}}
            )
            
            return document_id, filename
        except Exception as e:
            print(f"Error saving to file: {e}")
            return document_id, None
        
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