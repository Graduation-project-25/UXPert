from components.Suggestion_Component.suggestion import SuggestionInterface
from database.figma_features_repository import FigmaFeaturesRepository
from database.suggestions_repository import SuggestionsRepository


class RecognitionSuggestions(SuggestionInterface):
    
    def __init__(self):
        self.suggestion_repository = SuggestionsRepository()       
        self.figma_repository = FigmaFeaturesRepository()       


    def suggest_icon_label(self, is_icon_labeled, icon_text = "New Label"):
        if not is_icon_labeled:
            return {
                "suggestion": "Adding a label for better recognition",
                "action": "add_label",
                "new_properties": {"label_text": icon_text}
            }
        return {"suggestion": "Icons are already labeled - No change needed."}

    def suggest_icon_size(self, icon_width, icon_height):
        min_size = 23  # Minimum width allowed
        max_size = 32  # Maximum width allowed
        new_width = icon_width
        new_height = icon_height
        
        if icon_width < 24 or icon_height < 24:
            # Calculate the scale factor to maintain aspect ratio
            scale_factor = min_size / icon_width
            new_width = min_size
            new_height = round(icon_height * scale_factor)  # Maintain aspect ratio

        elif icon_width > 32 or icon_height > 32:
            # Calculate scale factor to reduce size proportionally
            scale_factor = max_size / icon_width
            new_width = max_size
            new_height = round(icon_height * scale_factor)  # Maintain aspect ratio
        return new_width, new_height
    
    def save_updated_elements(self,design_name, frame_name):
        saved_design = self.figma_repository.get_saved_design(design_name, frame_name)
        print(saved_design)

        if not saved_design:
            print(f"No data found for design '{design_name}', frame '{frame_name}'")
            return

        frames = saved_design.get("frames", [])
        if not frames:
            print(f"No frames found in design '{design_name}'")
            return

        for frame in frames:
            elements = frame.get("elements", [])
            for element in elements:  
                if element["name"].lower().startswith("ic"):
                    updated_icon_width, updated_icon_height = self.suggest_icon_size(element["width"], element["height"])
                    self.suggestion_repository.update_element_value(design_name, frame_name, element["id"],"width",updated_icon_width)
                    self.suggestion_repository.update_element_value(design_name, frame_name, element["id"],"height",updated_icon_height)


    def apply_suggestion():
        pass    
    def evaluate_with_suggestions():
        pass