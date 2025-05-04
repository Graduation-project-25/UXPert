import os
from dotenv import load_dotenv
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.modified_design_repository import ModifiedDesignsRepository
from database.suggestions_repository import SuggestionsRepository
import openai

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_key)

# Initialize database repositories
figma_repository = FigmaFeaturesRepository()
suggestions_repository = SuggestionsRepository()
feedback_repository = FeedbackRepository()
modified_designs_repo = ModifiedDesignsRepository()

# # Define output folder
# dataset_folder = './data/raw/EGFE'
# main_output_folder = dataset_folder + '/extractedFeatures'