from abc import ABC, abstractmethod

class UiProcessorInterface(ABC):

    @abstractmethod
    def save_ui_elements(self, elements, json_file,output_path):
        pass
    @abstractmethod
    def estimate_screen_size(self,image_name):
        pass
    @abstractmethod
    def aggregate_ui_elements(self, df):
        pass
