from abc import ABC, abstractmethod

class HeuristicEvaluationInterface(ABC):
    
    @abstractmethod
    def evaluate_rule(self, designs):
        pass
