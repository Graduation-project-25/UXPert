from sklearn.metrics import davies_bouldin_score, silhouette_score

from components.Clustering_Component.clustering_evaluation import ClusteringEvaluationInterface

class EGFEClusteringEvaluation(ClusteringEvaluationInterface):

    def evaluate_clustering(self,DBSCAN_dataset):
        # Evaluate clustering quality
        valid_labels = DBSCAN_dataset['Cluster']

        if len(valid_labels.unique()) > 1: 
        # Ensure there are enough clusters for evaluation 
            sil_score = silhouette_score(DBSCAN_dataset, valid_labels)
            db_score = davies_bouldin_score(DBSCAN_dataset, valid_labels)
            print(f"Silhouette Score: {sil_score}")
            print(f"Davies-Bouldin Index: {db_score}")
        else:
            print("Not enough clusters for evaluation metrics.")

