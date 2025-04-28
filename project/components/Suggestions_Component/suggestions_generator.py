from abc import ABC, abstractmethod

class SuggestionsGenerator(ABC):
    @abstractmethod
    def analyze_design(self):
        pass

    @abstractmethod
    def generate_suggested_image(self, generated_text_suggestions):
        pass
 
    @abstractmethod
    def generate_suggestions(self):
        pass
 