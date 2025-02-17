from database.base_repository import BaseRepository

class FeedbakRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["feedback"])
