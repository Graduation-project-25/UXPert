from pymongo import MongoClient 
from dotenv import load_dotenv
import os

import pymongo


class dbConfig:
    def __init__(self): 
        load_dotenv()
        self.mongo_uri = os.getenv('MONGO_URI')
        try:
            # Set a reasonable timeout and connection options
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=30000,  # 30 seconds to select server
                connectTimeoutMS=30000,          # 30 seconds to establish connection
                socketTimeoutMS=60000,           # 60 seconds for socket operations (includes writes)
                maxPoolSize=50                   # Adjust connection pool size if needed
            )
            # Verify connection
            self.client.server_info()
            print("Successfully connected to MongoDB server")
        except pymongo.errors.ConfigurationError as e:
            print(f"Configuration error: {e}")
            raise
        except pymongo.errors.ConnectionError as e:
            print(f"Connection error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise  

    def connect(self):
        return self.client["uxpert"]
        # collection = db["test"]

# Initialize Repository
# cluster_repo = ClusterRepository(db)

# Test
# document = {"name": "Test Cluster", "label": "rectangle", "color": "white"}
# isert = collection.insert_one(document)
# print("Sample Data Inserted!")

