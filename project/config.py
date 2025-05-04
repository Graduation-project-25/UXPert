from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.modified_design_repository import ModifiedDesignsRepository
from database.suggestions_repository import SuggestionsRepository

# Initialize database repositories
figma_repository = FigmaFeaturesRepository()
suggestions_repository = SuggestionsRepository()
feedback_repository = FeedbackRepository()
modified_designs_repo = ModifiedDesignsRepository()
