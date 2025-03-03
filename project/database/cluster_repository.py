from pymongo import MongoClient
from database.base_repository import BaseRepository
import pandas as pd

class ClusterRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["clusters"])

    def insert_cluster_data(self, clustered_data, design_name, cluster_type):
        """
        Updates existing cluster data if it exists for the given design and cluster type,
        otherwise inserts new cluster data.
        """
        if clustered_data.empty:
            print("Warning: clustered_data DataFrame is empty. Nothing to save.")
            return None

        # Prepare records to be inserted/updated
        records = clustered_data.to_dict(orient='records')
        for record in records:
            record['design_name'] = design_name
            record['cluster_type'] = cluster_type

        # Check if clusters already exist for this design and type
        filter_query = {"design_name": design_name, "cluster_type": cluster_type}
        existing_clusters = list(self.collection.find(filter_query))

        if existing_clusters:
            # Clusters exist, so replace them
            try:
                self.collection.delete_many(filter_query)  # Delete existing clusters
                self.collection.insert_many(records)  # Insert updated clusters
                print(f"Updated {len(records)} cluster records for '{design_name}' ({cluster_type}).")
                return True # return True to indicate an update
            except Exception as e:
                print(f"Error updating cluster data: {e}")
                return False # return false to indicate an error
        else:
            # Clusters don't exist, so insert new ones
            try:
                self.collection.insert_many(records)
                print(f"Inserted {len(records)} cluster records for '{design_name}' ({cluster_type}).")
                return True # return true to indicate an insert
            except Exception as e:
                print(f"Error inserting cluster data: {e}")
                return False # return false to indicate an error