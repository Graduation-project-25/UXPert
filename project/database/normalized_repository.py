from database.base_repository import BaseRepository

class NormalizedRepository(BaseRepository):
    def __init__(self):
        super().__init__("normalized data")
