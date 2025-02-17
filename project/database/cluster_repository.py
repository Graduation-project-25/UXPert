from database.base_repository import BaseRepository

class ClusterRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["clusters"])
