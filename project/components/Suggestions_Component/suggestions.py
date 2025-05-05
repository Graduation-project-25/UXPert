# import os
# from dotenv import load_dotenv
# import openai
# import base64
# from components.Suggestions_Component.prompt import Prompt
# from components.Suggestions_Component.suggestions_generator import SuggestionsGenerator


# class Suggestions(SuggestionsGenerator):
 
#     def __init__(self):
#         load_dotenv()  
#         self.openai_key = os.getenv("OPENAI_API_KEY")
#         self.design_image = "Project 2.png"
#         self.client = openai.OpenAI(api_key = self.openai_key)
#         self.prompt = Prompt(self.design_image)

#     def analyze_design(self):
#             # Read and encode the image file as base64
#             base64_image = self.get_base64_image()
#             # Create the chat completion request with the base64 image
#             response = self.client.chat.completions.create(
#                 model="gpt-4o",  # Vision model
#                 messages = self.prompt.get_gpt_4o_messages(base64_image)
#             )

#             # Print the response
#             gpt_suggestions = response.choices[0].message.content
#             return gpt_suggestions
    
#     def generate_suggested_image(self, generated_text_suggestions): 
#         print(generated_text_suggestions)

#         result = self.client.images.edit(
#             model="gpt-image-1",
#             image=open(self.design_image, "rb"),
#             prompt= self.prompt.get_gpt_image_1_prompt(generated_text_suggestions), 
#             quality = 'low',
#         )

#         image_base64 = result.data[0].b64_json
#         image_bytes = base64.b64decode(image_base64)

#         # Save the image to a file
#         with open("Project 2 - modified.png", "wb") as f:
#             f.write(image_bytes)

#     def get_base64_image(self):
#         with open(self.design_image, "rb") as image_file:
#             image_data = image_file.read()
#             base64_image = base64.b64encode(image_data).decode("utf-8")
#         return base64_image

#     def generate_suggestions(self):
#         generated_text_suggestions = self.analyze_design()
#         self.generate_suggested_image(generated_text_suggestions)


from datetime import datetime
import os
from bson import ObjectId
from dotenv import load_dotenv
import openai
import base64
from io import BytesIO
from components.Suggestions_Component.prompt import Prompt
from components.Suggestions_Component.suggestions_generator import SuggestionsGenerator
from config import suggestions_repository  # Import the repository

class Suggestions(SuggestionsGenerator):
 
    def __init__(self):
        load_dotenv()  
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.openai_key)
        self.prompt = Prompt()  # Remove image dependency from constructor

    def analyze_design(self, document_id):
        """Analyze design using image from database"""
        # Get the most recent image from the document
        image_doc = suggestions_repository.get_most_recent_image(document_id)
        
        if not image_doc or not image_doc.get("original_image"):
            raise ValueError("No image found in database document")
            
        # Extract base64 data (remove data URL prefix if present)
        base64_image = image_doc["original_image"]
        if base64_image.startswith("data:image"):
            base64_image = base64_image.split(",")[1]
            
        # Create the chat completion request
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.prompt.get_gpt_4o_messages(base64_image)
        )

        return response.choices[0].message.content
    
    def generate_suggested_image(self, document_id, generated_text_suggestions): 
        """Generate modified image using image from database"""
        # Get the most recent image from the document
        image_doc = suggestions_repository.get_most_recent_image(document_id)
        
        if not image_doc or not image_doc.get("original_image"):
            raise ValueError("No image found in database document")
            
        # Extract base64 data
        base64_image = image_doc["original_image"]
        if base64_image.startswith("data:image"):
            base64_image = base64_image.split(",")[1]
            
        # Convert to bytes and save temporarily (required by OpenAI API)
        image_bytes = base64.b64decode(base64_image)
        temp_image_path = "temp_db_image.png"
        with open(temp_image_path, "wb") as f:
            f.write(image_bytes)
            
        try:
            # Generate modified image
            result = self.client.images.edit(
                model="gpt-image-1",  # Using correct model name
                image=open(temp_image_path, "rb"),
                prompt=self.prompt.get_gpt_image_1_prompt(generated_text_suggestions),
                quality='low',
            )

            # Get the modified image
            modified_image_base64 = result.data[0].b64_json
            
            # Save modified image back to database
            suggestions_repository.update(
                {"_id": ObjectId(document_id)},
                {"$push": {"images": {
                    "modified_image": f"data:image/png;base64,{modified_image_base64}",
                    "timestamp": datetime.datetime.utcnow()
                }}}
            )
            
            return modified_image_base64
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    def generate_suggestions(self, document_id):
        """Main method to generate both text and image suggestions"""
        try:
            text_suggestions = self.analyze_design(document_id)
            modified_image = self.generate_suggested_image(document_id, text_suggestions)
            return {
                "text_suggestions": text_suggestions,
                "modified_image": modified_image
            }
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            raise