from abc import ABC, abstractmethod

class HeuristicTestingInterface(ABC):
    
    @abstractmethod
    def evaluate_rule_test(self, designs, evaluation_folder):
        pass

    @abstractmethod
    def analyze_test_results(self, train_json, test_json):
        pass
