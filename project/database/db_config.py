from pymongo import MongoClient 
from dotenv import load_dotenv
import os


class dbConfig:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv('MONGO_URI')
        self.client = MongoClient(self.mongo_uri)
    
    def connect(self):
        return self.client["uxpert"]
        # collection = db["test"]

# Initialize Repository
# cluster_repo = ClusterRepository(db)

# Test
# document = {"name": "Test Cluster", "label": "rectangle", "color": "white"}
# isert = collection.insert_one(document)
# print("Sample Data Inserted!")

