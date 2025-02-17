class BaseRepository:
    def __init__(self, collection):
        self.collection = collection

    def find_all(self):
        return list(self.collection.find({}))

    def find_by_id(self, id):
        return self.collection.find_one({"_id": id})

    def add(self, data):
        return self.collection.insert_one(data)

    def update(self, id, data):
        return self.collection.update_one({"_id": id}, {"$set": data})

    def delete(self, id):
        return self.collection.delete_one({"_id": id})
