from pymongo import MongoClient
from database.base_repository import BaseRepository
import pandas as pd

class ClusterRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["clusters"])

    def insert_cluster_data(self, clustered_data, cluster_type):
        """
        Updates existing cluster data if it exists for the given cluster type,
        otherwise inserts new cluster data.
        """
        if clustered_data.empty:
            print("Warning: clustered_data DataFrame is empty. Nothing to save.")
            return None

        # Prepare frames to be inserted/updated
        frames = clustered_data.to_dict(orient='records')

        # Check if clusters already exist for this cluster type
        filter_query = {"cluster_type": cluster_type}
        existing_clusters = list(self.collection.find(filter_query))

        if existing_clusters:
            # Clusters exist, so replace them
            try:
                self.collection.delete_many(filter_query)  # Delete existing clusters
                self.collection.insert_one({"cluster_type": cluster_type, "frames": frames})  # Insert updated clusters
                print(f"Updated {len(frames)} cluster frames for '{cluster_type}'.")
                return True  # return True to indicate an update
            except Exception as e:
                print(f"Error updating cluster data: {e}")
                return False  # return False to indicate an error
        else:
            # Clusters don't exist, so insert new ones
            try:
                self.collection.insert_one({"cluster_type": cluster_type, "frames": frames})
                print(f"Inserted {len(frames)} cluster frames for '{cluster_type}'.")
                return True  # return True to indicate an insert
            except Exception as e:
                print(f"Error inserting cluster data: {e}")
                return False  # return False to indicate an error