import os
from dotenv import load_dotenv
from database.feedback_repository import FeedbackRepository
from database.figma_features_repository import FigmaFeaturesRepository
from database.modified_design_repository import ModifiedDesignsRepository
import openai
from openai import OpenAI

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize database repositories
figma_repository = FigmaFeaturesRepository()
feedback_repository = FeedbackRepository()
modified_designs_repo = ModifiedDesignsRepository()

# Define output folder
dataset_folder = './data/raw/EGFE'
main_output_folder = dataset_folder + '/extractedFeatures'