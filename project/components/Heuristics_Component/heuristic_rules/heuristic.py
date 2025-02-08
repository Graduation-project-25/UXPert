from abc import ABC, abstractmethod

class HeuristicInterface(ABC):
    
    @abstractmethod
    def evaluate_rule(self, cluster_data):
        pass
