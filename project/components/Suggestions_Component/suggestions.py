import os
from dotenv import load_dotenv
import openai
import base64, binascii
from components.Suggestions_Component.prompt import Prompt
from components.Suggestions_Component.suggestions_generator import SuggestionsGenerator


class Suggestions(SuggestionsGenerator):
 
    def __init__(self, frame_image):
        load_dotenv()  
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key = self.openai_key)
        self.frame_image = frame_image
        # self.design_image = "Project 1.png"
        self.design_image = self.convert_base64_to_png(frame_image)
        self.prompt = Prompt(self.design_image)
        
    def analyze_design(self):
        # Read and encode the image file as base64
        # base64_image = self.get_base64_image()
        # base64_image = str(self.frame_image).split(",")[1]
        base64_image = self.get_base64_string(self.frame_image)

        # Create the chat completion request with the base64 image
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Vision model
            messages = self.prompt.get_gpt_4o_messages(base64_image)
        )  

        # Print the response
        gpt_suggestions = response.choices[0].message.content
        return gpt_suggestions
    
    def generate_suggested_image(self, generated_text_suggestions): 
        print(generated_text_suggestions)

        result = self.client.images.edit(
            model="gpt-image-1",
            image=open(self.design_image, "rb"),
            prompt= self.prompt.get_gpt_image_1_prompt(generated_text_suggestions), 
            # quality = 'high',
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Save the image to a file
        with open("test2-modified.png", "wb") as f:
            f.write(image_bytes)

    def get_base64_string(self, data_url):
        try:
            return str(data_url).split(",")[1]
        except IndexError:
            print("Error: Invalid data URL format")
            return None
        
    
    def convert_base64_to_png(self, data_url):
        try:
            base64_string = self.get_base64_string(data_url)
            image = base64.b64decode(base64_string, validate=True)
            file_to_save = "converted_image.png"
            with open(file_to_save, "wb") as f:
                f.write(image)
            return file_to_save
        except binascii.Error as e:
            print(e)


    # def get_base64_image(self):
    #     with open(self.design_image, "rb") as image_file:
    #         image_data = image_file.read()
    #         base64_image = base64.b64encode(image_data).decode("utf-8")
    #     return base64_image

    def generate_suggestions(self):
        generated_text_suggestions = self.analyze_design()
        self.generate_suggested_image(generated_text_suggestions)
