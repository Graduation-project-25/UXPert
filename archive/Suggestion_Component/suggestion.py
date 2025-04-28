from abc import ABC, abstractmethod

class SuggestionInterface(ABC):
    
    @abstractmethod
    def evaluate_with_suggestions(self, elements, screen_width, screen_height):
        pass

    @abstractmethod
    def apply_suggestion(self, elements, suggestion):
        pass

    
