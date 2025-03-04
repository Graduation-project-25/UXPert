from database.base_repository import BaseRepository

class FeedbakRepository(BaseRepository):
    def __init__(self):
        super().__init__("feedback")
