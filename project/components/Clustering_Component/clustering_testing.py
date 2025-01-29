from abc import ABC, abstractmethod

class ClusteringTestingInterface(ABC):
    
    @abstractmethod
    def assign_test_clusters(self,X_train, X_test, dbscan):
        pass

    @abstractmethod
    def evaluate_test_clusters(self,X_test, X_train):
        pass
