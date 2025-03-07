from database.base_repository import BaseRepository

class ClusterRepository(BaseRepository):
    def __init__(self):
        super().__init__("clusters")


    def insert_cluster_data(self, clustered_data, cluster_type, batch_size=1000):
        if clustered_data.empty:
            print("Warning: clustered_data DataFrame is empty. Nothing to save.")
            return None

        new_frames = clustered_data.to_dict(orient='records')
        total_new = len(new_frames)
        filter_query = {"cluster_type": cluster_type}
        existing_clusters = list(self.find_all(filter_query))

        try:
            if existing_clusters:
                existing_frames = existing_clusters[0].get("frames", [])
                updated_frames = existing_frames.copy()

                # Process in batches
                for i in range(0, total_new, batch_size):
                    batch = new_frames[i:i + batch_size]
                    updated_frames.extend(batch)
                    self.delete_all(filter_query)
                    self.add({"cluster_type": cluster_type, "frames": updated_frames})
                    print(f"Processed batch {i // batch_size + 1}: {len(batch)} frames")

                print(f"Updated {total_new} cluster frames for '{cluster_type}'. Total: {len(updated_frames)}")
                return True
            else:
                # Initial insert in batches
                for i in range(0, total_new, batch_size):
                    batch = new_frames[i:i + batch_size]
                    self.add({"cluster_type": cluster_type, "frames": batch})
                    print(f"Inserted batch {i // batch_size + 1}: {len(batch)} frames")
                print(f"Inserted {total_new} cluster frames for '{cluster_type}'.")
                return True
        except Exception as e:
            print(f"Error updating cluster data: {e}")
            return False