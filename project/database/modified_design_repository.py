# modified_designs_repository.py
from database.base_repository import BaseRepository
import os
import json
from datetime import datetime

class ModifiedDesignsRepository(BaseRepository):
    def __init__(self):
        super().__init__("modified_designs")
        
    def save_modification_record(self, original_data, modified_json):
        """
        Save complete modification record including:
        - Original design
        - AI analysis (modifications)
        - Modified design (with changes applied)
        Returns:
            tuple: (document_id, files_dict) where files_dict contains string paths
        """
        document = {
            "original": {
                "design_name": original_data.get('design_name', 'Untitled'),
                "user_name": original_data.get('user_name', 'Unknown'),
                "design_json": original_data['design_json'],
                "timestamp": datetime.utcnow()
            },
            "analysis": modified_json.get('modifications', []),
            "modified_design": modified_json.get('modified_design', {}),
            "files": {
                "original_saved": False,
                "modified_saved": False,
                "analysis_saved": False
            }
        }
        
        # Save to database first
        result = self.add(document)
        document_id = str(result.inserted_id)
        
        # Prepare files dictionary (strings only)
        files_dict = {
            "original": None,
            "modified": None,
            "analysis": None
        }
        
        # Save to filesystem
        try:
            os.makedirs("modified_designs", exist_ok=True)
            base_path = f"modified_designs/{document_id}"
            
            # Save and record paths
            original_path = f"{base_path}_original.json"
            with open(original_path, 'w') as f:
                json.dump(original_data, f, indent=2)
            files_dict["original"] = original_path
            
            modified_path = f"{base_path}_modified.json"
            with open(modified_path, 'w') as f:
                json.dump(modified_json['modified_design'], f, indent=2)
            files_dict["modified"] = modified_path
            
            analysis_path = f"{base_path}_analysis.json"
            with open(analysis_path, 'w') as f:
                json.dump(modified_json['modifications'], f, indent=2)
            files_dict["analysis"] = analysis_path
            
            # Update document with string paths only
            self.update(
                {"_id": result.inserted_id},
                {"$set": {"files": files_dict}}
            )
            
        except Exception as e:
            print(f"File save error: {e}")
    
        return document_id, files_dict  # Now returns strings only
        
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