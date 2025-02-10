from abc import ABC, abstractmethod

class ClusteringInterface(ABC):

    @abstractmethod
    def dbscan_cluster(self, feature):
        pass

    @abstractmethod
    def handle_outliers(self, X_train, cluster_csv, outliers_csv):
        pass

    @abstractmethod
    def save_cluster_as_json(self,clusters,cluster_json_path, group_by):
        pass

    # @abstractmethod
    # def calculate_nearest_neighbours(X_train_selected, percentile, n_neighbors=5):
    #     pass

