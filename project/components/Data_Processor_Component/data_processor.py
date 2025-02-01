from abc import ABC, abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def process(self):
        pass
    