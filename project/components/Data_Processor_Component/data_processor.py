from abc import ABC, abstractmethod
import os
import shutil

class DataProcessor(ABC):
    @abstractmethod
    def process(self):
        pass
    