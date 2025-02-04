from abc import ABC, abstractmethod

class SizeEstimatorInterface(ABC):
    @abstractmethod
    def estimate_screen_size(self,image_name):
        pass
    @abstractmethod
    def _calculate_mean_size(self):
        pass
