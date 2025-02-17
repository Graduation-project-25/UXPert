from database.base_repository import BaseRepository

class FigmaFeaturesRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["figma features"])
