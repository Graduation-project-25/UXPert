from abc import ABC, abstractmethod

class UiNormalizerInterface(ABC):
    @abstractmethod
    def normalize_ui_elements(self, elements):
        pass

    @abstractmethod
    def normalize_screen_size(self,screen_size):
        pass
