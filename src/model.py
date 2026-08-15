import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

class SegmentationModel:
    def __init__(self, n_components: int = 2, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self.pca = PCA(n_components=n_components, random_state=random_state)

    def apply_pca(self, X_scaled):
        X_pca = self.pca.fit_transform(X_scaled)
        explained_variance = float(sum(self.pca.explained_variance_ratio_) * 100)
        return X_pca, explained_variance

    def find_optimal_k(self, X_pca, k_range=range(2, 9)):
        inertia_list = []
        silhouette_list = []

        for k in k_range:
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            km.fit(X_pca)
            inertia_list.append(km.inertia_)
            silhouette_list.append(silhouette_score(X_pca, km.labels_))

        return list(k_range), inertia_list, silhouette_list

    def fit_predict(self, X_pca, k: int = 6):
        final_kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
        cluster_labels = final_kmeans.fit_predict(X_pca)
        return cluster_labels, final_kmeans

def auto_label_clusters(df: pd.DataFrame, skill_cols: list, cluster_col: str = 'Cluster', top_n: int = 3) -> tuple[dict, pd.DataFrame]:
    """Küme merkezlerini genel populasyon ortalamasına göre analiz edip dinamik etiketler oluşturur."""
    cluster_means = df.groupby(cluster_col)[skill_cols].mean()
    global_means = df[skill_cols].mean()
    global_std = df[skill_cols].std()

    # Z-Score farkı ile bağımsız yetenek sapmasını bulma
    relative_diff = (cluster_means - global_means) / global_std
    cluster_label_map = {}

    for cluster_id in relative_diff.index:
        top_skills = relative_diff.loc[cluster_id].nlargest(top_n).index.tolist()
        clean_skills = [
            skill.replace('defending_', '')
                 .replace('mentality_', '')
                 .replace('movement_', '')
                 .replace('skill_', '')
                 .replace('power_', '')
                 .replace('_', ' ')
                 .title()
            for skill in top_skills
        ]
        label = f"Cluster {cluster_id}: {', '.join(clean_skills)}"
        cluster_label_map[cluster_id] = label

    df['Cluster_Role'] = df[cluster_col].map(cluster_label_map)
    return cluster_label_map, df