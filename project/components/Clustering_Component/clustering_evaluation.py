from abc import ABC, abstractmethod

class ClusteringEvaluationInterface(ABC):
    
    @abstractmethod
    def evaluate_clustering(self,DBSCAN_dataset):
        pass
