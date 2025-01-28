from abc import ABC, abstractmethod

class FeatureExtractorInterface(ABC):
    @abstractmethod
    def extract_json_file_path(self, json_folder, limit=50):
        pass

    @abstractmethod
    def extract_ui_elements(self, json_file_path):
        pass

    @abstractmethod
    def normalize_ui_elements(self, elements, df):
        pass

    @abstractmethod
    def save_ui_elements(self, elements, output_path):
        pass

    @abstractmethod
    def aggregate_ui_elements(self, df):
        pass

    @abstractmethod
    def split_dataset(self, df):
        pass
