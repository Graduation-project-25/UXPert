from database.base_repository import BaseRepository

class NormalizedRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["normalized data"])
