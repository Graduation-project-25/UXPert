from database.base_repository import BaseRepository

class ClusterRepository(BaseRepository):
    def __init__(self):
        super().__init__("clusters")


    def insert_cluster_data(self, clustered_data, cluster_type):
        if clustered_data.empty:
            print("Warning: clustered_data DataFrame is empty. Nothing to save.")
            return None
 
        # Prepare frames to be inserted/updated
        frames = clustered_data.to_dict(orient='records')
        # print(frames)
        # print("*******************************************************")

        # Check if clusters already exist for this cluster type
        filter_query = {"cluster_type": cluster_type}
        existing_clusters = list(self.find_all(filter_query))

        if existing_clusters:
            # Clusters exist, so replace them
            try:
                self.delete_all(filter_query)  # Delete existing clusters
                self.add({"cluster_type": cluster_type, "frames": frames})  # Insert updated clusters
                print(f"Updated {len(frames)} cluster frames for '{cluster_type}'.")
                return True  # return True to indicate an update
            except Exception as e:
                print(f"Error updating cluster data: {e}")
                return False  # return False to indicate an error
        else:
            # Clusters don't exist, so insert new ones
            try:
                self.add({"cluster_type": cluster_type, "frames": frames})
                print(f"Inserted {len(frames)} cluster frames for '{cluster_type}'.")
                return True  # return True to indicate an insert
            except Exception as e:
                print(f"Error inserting cluster data: {e}")
                return False  # return False to indicate an error