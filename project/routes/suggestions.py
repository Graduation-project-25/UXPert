import os
from dotenv import load_dotenv
import openai
import base64

from routes.prompt import Prompt

class Suggestions:
    load_dotenv()  
    openai_key = os.getenv("OPENAI_API_KEY")

    def __init__(self):
        self.client = openai.OpenAI(api_key = self.openai_key)
        self.prompt = Prompt()

    def generate_image(self):
        result = self.client.images.generate(
            model="gpt-image-1",
            prompt= self.prompt.get_gpt_image_1_prompt("Project 1.png"),   
            quality = 'low',
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Save the image to a file
        with open("modified.png", "wb") as f:
            f.write(image_bytes)

