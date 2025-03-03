from pymongo import MongoClient
from database.base_repository import BaseRepository
import pandas as pd

class ClusterRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["clusters"])

    def insert_cluster_data(self, clustered_data, design_name, cluster_type):
        if clustered_data.empty:
            print("Warning: clustered_data DataFrame is empty. Nothing to save.")
            return

        records = clustered_data.to_dict(orient='records')

        # Add design_name and cluster_type to each record
        for record in records:
            record['design_name'] = design_name
            record['cluster_type'] = cluster_type

        try:
            self.collection.insert_many(records)
            print(f"Inserted {len(records)} cluster records for '{design_name}' ({cluster_type}).")
        except Exception as e:
            print(f"Error inserting cluster data: {e}")

    def clear_clusters_for_design_type(self, design_name, cluster_type):
        try:
            result = self.collection.delete_many({"design_name": design_name, "cluster_type": cluster_type})
            print(f"Deleted {result.deleted_count} cluster records for '{design_name}' ({cluster_type}).")
        except Exception as e:
            print(f"Error deleting cluster data: {e}")