from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB URI
mongo_uri = os.getenv('MONGO_URI')

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["uxpert"]

# Initialize Repository
# cluster_repo = ClusterRepository(db)

# Test
# cluster_repo.create({"name": "Test Cluster", "label": "rectangle", "color": "white"})
# print("Sample Data Inserted!")

