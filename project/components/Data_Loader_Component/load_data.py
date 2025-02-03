from abc import ABC, abstractmethod

class LoadDataInterface(ABC):
    
    @abstractmethod
    def load_train_data(self):
        pass
