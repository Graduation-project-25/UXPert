import os
import tempfile
from dotenv import load_dotenv
import openai
import base64, binascii
from components.Suggestions_Component.prompt import Prompt
from components.Suggestions_Component.suggestions_generator import SuggestionsGenerator
from database.suggestions_repository import SuggestionsRepository
import hashlib


class Suggestions(SuggestionsGenerator):

    def __init__(self, frame_image, feature_data):
        load_dotenv()  
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key = self.openai_key)
        self.suggestions_repository = SuggestionsRepository()
        self.frame_image = frame_image
        self.feature_data = feature_data
        self.design_image = self.convert_base64_to_png(frame_image)
        self.current_image_hash = self._calculate_image_hash(frame_image)
        self.prompt = Prompt(self.design_image)

    def analyze_design(self):
        # Check if we have existing suggestions for this image hash
        existing_hash = self.suggestions_repository.get_image_hash_for_frame(
            self.feature_data["design_name"],
            self.feature_data.get("frame_id"),
            self.feature_data.get("user_name")
        )
        
        existing_suggestions = self.suggestions_repository.get_suggestions_for_frame(
            self.feature_data["design_name"],
            self.feature_data.get("frame_id"),
            self.feature_data.get("user_name")
        )
        
        # Only generate new suggestions if the image has changed or we don't have suggestions
        if existing_hash != self.current_image_hash or not existing_suggestions:
            base64_image = self.get_base64_string(self.frame_image)
            if not base64_image:
                raise ValueError("Invalid image data format")

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.prompt.get_gpt_4o_messages(base64_image)
            )

            gpt_suggestions = response.choices[0].message.content

            self.suggestions_repository.save_text_suggestions(
                self.feature_data,
                gpt_suggestions
            )
            self.suggestions_repository.update_textual_suggestion(self.feature_data, self.current_image_hash)            
            return gpt_suggestions
        else:
            return existing_suggestions
    
    def generate_suggested_image(self, generated_text_suggestions):
        try:
            # Check if we already have a modified image for this hash
            existing_hash = self.suggestions_repository.get_image_hash_for_frame(
                self.feature_data["design_name"],
                self.feature_data.get("frame_id"),
                self.feature_data.get("user_name")
            )
            
            if existing_hash == self.current_image_hash:
                # Try to get existing modified image
                existing_image = self.suggestions_repository.get_modified_image(
                    self.feature_data["design_name"],
                    self.feature_data.get("frame_id"),
                    self.feature_data.get("user_name")
                )
                if existing_image:
                    if existing_image.startswith('data:image'):
                        return existing_image.split(',')[1]
                    return existing_image
            
            # If we get here, we need to generate a new image
            print("Generating new suggested image...")
            
            screen_width = self.feature_data.get("screen_width")
            screen_height = self.feature_data.get("screen_height")

            supported_sizes = [
                (1024, 1024),  # 1.0
                (1024, 1536),  # 0.667
                (1536, 1024),  # 1.5
            ]
            original_aspect = screen_width / screen_height

            # Calculate differences in aspect ratios and sort to find the closest
            aspect_differences = [
                (abs(original_aspect - (w / h)), (w, h))
                for w, h in supported_sizes
            ]
            aspect_differences.sort(key=lambda x: x[0])  # Sort by difference
            target_size = aspect_differences[0][1]  # Take the size with smallest difference
            target_width, target_height = target_size

            with open(self.design_image, "rb") as image_file:
                result = self.client.images.edit(
                    model="gpt-image-1", 
                    image=image_file,
                    size=f"{target_width}x{target_height}",
                    prompt=self.prompt.get_gpt_image_1_prompt(generated_text_suggestions)
                )

            modified_image_b64 = result.data[0].b64_json
            
            # Save to database with the current hash
            save_result = self.suggestions_repository.save_modified_image(
                self.feature_data,
                modified_image_data=modified_image_b64,
                image_hash=self.current_image_hash
            )
            
            if not save_result:
                raise Exception("Failed to save image to database")
                
            return modified_image_b64
            
        except Exception as e:
            print(f"Error generating suggested image: {str(e)}")
            raise
                     
    def get_base64_string(self, data_url):
        try:
            return str(data_url).split(",")[1]
        except IndexError:
            print("Error: Invalid data URL format")
            return None
        
    def _calculate_image_hash(self, image_data):
        """Calculate a hash of the image data for change detection"""
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        return hashlib.sha256(image_bytes).hexdigest()
        
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