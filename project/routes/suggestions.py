import os
from dotenv import load_dotenv
import openai
import base64

from routes.prompt import Prompt

class Suggestions:
    load_dotenv()  
    openai_key = os.getenv("OPENAI_API_KEY")
    design_image = "Project 1.png"

    def __init__(self):
        self.client = openai.OpenAI(api_key = self.openai_key)
        self.prompt = Prompt(self.design_image)

    # Create the prompt based on GPT-4o suggestions
    def generate_suggested_image(self, gpt_suggestions): 
        print(gpt_suggestions)

        result = self.client.images.edit(
            model="gpt-image-1",
            image=open(self.design_image, "rb"),
            prompt= self.prompt.get_gpt_image_1_prompt(gpt_suggestions), 
            quality = 'low',
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Save the image to a file
        with open("Project 1 - modified.png", "wb") as f:
            f.write(image_bytes)

    def analyze_design(self):
            # Read and encode the image file as base64
            base64_image = self.get_base64_image()
            # Create the chat completion request with the base64 image
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Vision model
                messages = self.prompt.get_gpt_4o_messages(base64_image)
            )

            # Print the response
            gpt_suggestions = response.choices[0].message.content
            return gpt_suggestions
    
    def get_base64_image(self):
        with open(self.design_image, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
        return base64_image

