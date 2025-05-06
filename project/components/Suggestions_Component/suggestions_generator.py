from abc import ABC, abstractmethod

class SuggestionsGenerator(ABC):
    @abstractmethod
    def analyze_design(self, document_id):
        pass

    @abstractmethod
    def generate_suggested_image(self, document_id,generated_text_suggestions):
        pass
 
    @abstractmethod
    def generate_suggestions(self, document_id):
        pass
 