from abc import ABC, abstractmethod

class DataSplitterInterface(ABC):
    @abstractmethod
    def get_json_files(self):
        pass
    @abstractmethod
    def save_split_files(self, train_folder, test_folder):
        pass