from database.base_repository import BaseRepository

class SuggestionsRepository(BaseRepository):
    def __init__(self):
        super().__init__("suggestions")
