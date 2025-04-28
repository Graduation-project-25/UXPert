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

    def generate_image(self, img): 
        gpt_suggestions = self.analyze_design(img)
        print(gpt_suggestions)

        result = self.client.images.generate(
            model="gpt-image-1",
            prompt = f"Redesign the UX/UI design. {gpt_suggestions}",
            # prompt= self.prompt.get_gpt_image_1_prompt("Project 1.png"), 
            size = "1024x1024",  
            quality = 'low',
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Save the image to a file
        with open("modified.png", "wb") as f:
            f.write(image_bytes)

    def analyze_design(self, image_file_path):
            # Step 1: Read and encode the image file as base64
            with open(image_file_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")

            # Step 2: Create the chat completion request with the base64 image
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Vision model
                messages = self.prompt.get_gpt_4o_messages(base64_image)
            )

            # Step 3: Print the response
            gpt_suggestions = response.choices[0].message.content
            return gpt_suggestions