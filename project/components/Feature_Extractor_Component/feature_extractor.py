from abc import ABC, abstractmethod

class FeatureExtractorInterface(ABC):
    @abstractmethod
    def extract_json_file_paths(self, json_folder):
        pass

    @abstractmethod
    def extract_ui_elements(self, json_file_path):
        pass

    @abstractmethod
    def extract_elements_and_screen_size (self, json_file_path):
        pass

