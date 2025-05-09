import os
import tempfile
from dotenv import load_dotenv
import openai
import base64, binascii
from components.Suggestions_Component.prompt import Prompt
from components.Suggestions_Component.suggestions_generator import SuggestionsGenerator
from database.suggestions_repository import SuggestionsRepository



class Suggestions(SuggestionsGenerator):
 
    def __init__(self, frame_image, feature_data):
        load_dotenv()  
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key = self.openai_key)
        self.frame_image = frame_image
        self.feature_data = feature_data
        self.suggestions_repository = SuggestionsRepository()
        self.design_image = self.convert_base64_to_png(frame_image)
        self.prompt = Prompt(self.design_image)
        
    def analyze_design(self):
        # Read and encode the image file as base64
        base64_image = self.get_base64_string(self.frame_image)
        if not base64_image:
            raise ValueError("Invalid image data format")

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

        modified_image_b64 = result.data[0].b64_json
        modified_image_url = base64.b64decode(modified_image_b64)
            
       
    
    # Save base64 string directly, not decoded binary
        self.suggestions_repository.save_modified_image(
            design_name=self.feature_data["design_name"],
            user_name=self.feature_data.get("user_name", "Unknown User"),
            frame_id=self.feature_data.get("frame_id"),
            modified_image_data=modified_image_b64  # Save the base64 string directly
        )
        # Optional: Save to local file
        with open("modified_output.png", "wb") as f:
            f.write(base64.b64decode(modified_image_b64))
        # Return the base64 string for immediate use
        return modified_image_b64
            
        
            
            
    def get_base64_string(self, data_url):
        try:
            return str(data_url).split(",")[1]
        except IndexError:
            print("Error: Invalid data URL format")
            return None
        
    
    # def convert_base64_to_png(self, data_url):
    #     try:
    #         base64_string = self.get_base64_string(data_url)
    #         image = base64.b64decode(base64_string, validate=True)
    #         file_to_save = "converted_image2.png"
    #         with open(file_to_save, "wb") as f:
    #             f.write(image)
    #         return file_to_save
    #     except binascii.Error as e:
    #         print(e)


    def convert_base64_to_png(self, data_url):
        try:
            base64_string = self.get_base64_string(data_url)
            image = base64.b64decode(base64_string, validate=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(image)
                temp_file_path = temp_file.name
            return temp_file_path
        except binascii.Error as e:
            print(e)
            return None

    def generate_suggestions(self):
        generated_text_suggestions = self.analyze_design()
        self.generate_suggested_image(generated_text_suggestions)

    def __del__(self):
        """Destructor to clean up the temporary file."""
        if hasattr(self, 'design_image') and self.design_image and os.path.exists(self.design_image):
            try:
                os.unlink(self.design_image)
                print(f"Deleted temporary file: {self.design_image}")
            except OSError as e:
                print(f"Error deleting temporary file {self.design_image}: {e}")
