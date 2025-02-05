from abc import ABC, abstractmethod

class LoadDataInterface(ABC):
    
    @abstractmethod
    def load_data(self):
        pass
