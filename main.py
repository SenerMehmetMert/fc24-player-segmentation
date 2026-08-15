import os
from src.data_preprocessing import DataPreprocessor
from src.model import SegmentationModel, auto_label_clusters
from src.visualization import Visualizer
import pandas as pd


def main():
  os.makedirs('outputs', exist_ok=True)

  print('[1/6] Veri işleniyor ve standartlaştırılıyor...')
  preprocessor = DataPreprocessor('data/players_24.csv')
  df_field, X_scaled, valid_skills = preprocessor.process()

  print('[2/6] PCA modeli uygulanıyor...')
  model = SegmentationModel()
  X_pca, var_ratio = model.apply_pca(X_scaled)
  print(f'PCA 2 Bileşenin Toplam Açıklanan Varyansı: %{var_ratio:.2f}')

  print('[3/6] Optimal K analizi grafikleri oluşturuluyor...')
  k_list, inertia_list, silhouette_list = model.find_optimal_k(X_scaled)
  Visualizer.plot_elbow_and_silhouette(
      k_list, inertia_list, silhouette_list, 'outputs/elbow_silhouette.png'
  )

  print('[4/6] K-Means (K=6) eğitiliyor ve etiketleniyor...')
  clusters, _ = model.fit_predict(X_scaled, k=6)

  df_field['Cluster'] = clusters
  df_field['PCA1'] = X_pca[:, 0]
  df_field['PCA2'] = X_pca[:, 1]

  cluster_map, df_field = auto_label_clusters(
      df_field, valid_skills, cluster_col='Cluster', top_n=3
  )

  print('\n--- Tespit Edilen Küme Etiketleri ---')
  for k_id, label in cluster_map.items():
    print(f'• {label}')
  print('-------------------------------------\n')

  Visualizer.plot_clusters(
      df_field, 'outputs/player_clusters_pca.png', top_n_per_cluster=2
  )

  print('[5/6] Genel sonuçlar ve özetler kaydediliyor...')
  cluster_summary = df_field.groupby('Cluster')[valid_skills].mean().T
  cluster_summary.to_csv('outputs/cluster_summary.csv')
  df_field.to_csv('outputs/processed_players.csv', index=False)

  print(
      '[6/6] Her küme için en iyi 100 oyuncu ayrı CSV dosyalarına'
      ' aktarılıyor...'
  )
  for c_id in sorted(df_field['Cluster'].unique()):
    top100_df = (
        df_field[df_field['Cluster'] == c_id]
        .sort_values(by='overall', ascending=False)
        .head(100)
    )
    file_path = f'outputs/cluster_{c_id}_top100.csv'
    top100_df.to_csv(file_path, index=False)
    print(f'  ✅ Küme {c_id} Top 100 kaydedildi -> {file_path}')

  print('\n--- TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI ---')


if __name__ == '__main__':
  main()