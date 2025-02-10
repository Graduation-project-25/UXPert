from abc import ABC, abstractmethod

class LoadDataInterface(ABC):
    
    @abstractmethod
    def load_data(self, data_folder):
        pass
    @abstractmethod
    def load_unnormalized_data(self, data_folder):
        pass
