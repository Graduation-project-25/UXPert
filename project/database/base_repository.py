from bson import ObjectId
from database.db_config import dbConfig
 
class BaseRepository:
    def __init__(self, collection):
        db_config = dbConfig()
        db = db_config.connect()
        self.collection = db[collection]

    def find_all(self, filter_query):
        return list(self.collection.find(filter_query))
    def find_by_id(self, id):
        return self.collection.find_one({"_id": ObjectId(id)})
    
    def find_one(self, filter_query, projection=None):
        return self.collection.find_one(filter_query, projection)

    def add(self, data): 
        return self.collection.insert_one(data)

    def update(self, filter_query, update_query, upsert=False, array_filters=None):
        return self.collection.update_one(
            filter_query, 
            update_query, 
            upsert=upsert, 
            array_filters=array_filters
        )  
      
    def delete(self, id):
        return self.collection.delete_one({"_id": ObjectId(id)})
 
    def delete_all(self, filter_query):
        return self.collection.delete_many(filter_query)
 