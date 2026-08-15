import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class Visualizer:
    @staticmethod
    def plot_elbow_and_silhouette(k_list, inertia_list, silhouette_list, save_path: str):
        fig, ax = plt.subplots(1, 2, figsize=(14, 5))

        ax[0].plot(k_list, inertia_list, marker='o', color='#1f77b4', linewidth=2)
        ax[0].set_title('Elbow Yöntemi (Inertia)', fontsize=12, fontweight='bold')
        ax[0].set_xlabel('Küme Sayısı (K)')
        ax[0].set_ylabel('Inertia (WCSS)')
        ax[0].grid(True, linestyle='--', alpha=0.6)

        ax[1].plot(k_list, silhouette_list, marker='s', color='#2ca02c', linewidth=2)
        ax[1].set_title('Silhouette Skorları', fontsize=12, fontweight='bold')
        ax[1].set_xlabel('Küme Sayısı (K)')
        ax[1].set_ylabel('Silhouette Skoru')
        ax[1].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    @staticmethod
    def plot_clusters(df_field: pd.DataFrame, save_path: str, top_n_per_cluster: int = 2):
        plt.figure(figsize=(13, 8))
        
        hue_col = 'Cluster_Role' if 'Cluster_Role' in df_field.columns else 'Cluster'
        name_col = 'short_name' if 'short_name' in df_field.columns else 'Name'
        overall_col = 'overall' if 'overall' in df_field.columns else 'Overall'

        sns.scatterplot(
            x='PCA1', y='PCA2', 
            hue=hue_col, data=df_field, 
            palette='tab10', alpha=0.6, s=50
        )

        # TEKİLLEŞTİRME: Aynı isimdeki oyuncuları süzüp en yüksek reytingli olanı seçme
        df_unique = df_field.sort_values(overall_col, ascending=False).drop_duplicates(subset=[name_col])

        # Dinamik Etiketleme: Her kümenin en yüksek reytingli benzersiz oyuncularını seçme
        star_players_df = df_unique.groupby('Cluster', group_keys=False).apply(
            lambda x: x.nlargest(top_n_per_cluster, overall_col)
        )

        for _, player in star_players_df.iterrows():
            x_pos = player['PCA1']
            y_pos = player['PCA2']
            player_name = player[name_col]

            plt.scatter(x_pos, y_pos, color='black', s=120, zorder=5)
            plt.annotate(
                player_name, 
                (x_pos, y_pos), 
                fontsize=9, fontweight='bold', 
                xytext=(5, 5), textcoords='offset points'
            )

        plt.title('EA Sports FC 24 Oyuncu Segmentasyonu - K-Means & PCA', fontsize=14, fontweight='bold')
        plt.xlabel('PCA 1 (Hücum / Fizik Aksı)')
        plt.ylabel('PCA 2 (Savunma / Oyun Kurma Aksı)')
        plt.legend(title='Küme Rolleri', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()