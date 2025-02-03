from abc import ABC, abstractmethod

class ClusteringInterface(ABC):

    @abstractmethod
    def dbscan_cluster(self):
        pass

    @abstractmethod
    def handle_outliers(self, X_train, cluster_csv, outliers_csv):
        pass

    @abstractmethod
    def analyze_clusters(self, df):
        pass

    @abstractmethod
    def save_cluster_as_json(self,clusters,cluster_json_path, group_by):
        pass
