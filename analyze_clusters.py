import pandas as pd

def analyze():
    summary_df = pd.read_csv('outputs/cluster_summary.csv', index_col=0)
    players_df = pd.read_csv('outputs/processed_players.csv', low_memory=False)

    name_col = 'short_name' if 'short_name' in players_df.columns else 'Name'
    overall_col = 'overall' if 'overall' in players_df.columns else 'Overall'

    print("=" * 70)
    print("EA SPORTS FC 24 - K-MEANS KÜME PROFİL ANALİZİ (K=6)")
    print("=" * 70 + "\n")

    markdown_rows = []

    for cluster_id in sorted(summary_df.columns, key=lambda x: int(x)):
        cid = int(cluster_id)
        cluster_data = players_df[players_df['Cluster'] == cid]
        player_count = len(cluster_data)

        # Küme Rolü İsimlendirmesi
        role_name = cluster_data['Cluster_Role'].iloc[0] if 'Cluster_Role' in cluster_data.columns else f"Cluster {cid}"

        # En yüksek ortalamaya sahip ilk 5 özellik
        top_skills = summary_df[cluster_id].nlargest(5)
        top_skills_str = ", ".join([f"{skill} ({val:.1f})" for skill, val in top_skills.items()])

        # En yüksek reytingli 3 temsilci oyuncu
        top_players = cluster_data.nlargest(3, overall_col)[name_col].tolist()
        top_players_str = ", ".join(top_players)

        print(f" {role_name} (Oyuncu Sayısı: {player_count})")
        print(f"   • En Yüksek Ortalamalı Yetenekler: {top_skills_str}")
        print(f"   • Örnek Oyuncular: {top_players_str}\n")

        markdown_rows.append({
            "Küme Kimliği": f"Küme {cid}",
            "Otomatik Profil Etiketi": role_name,
            "Oyuncu Sayısı": player_count,
            "Örnek Yıldız Oyuncular": top_players_str
        })

    md_df = pd.DataFrame(markdown_rows)
    print("=" * 70)
    print("MEDIUM İÇİN MARKDOWN TABLOSU")
    print("=" * 70)
    print(md_df.to_markdown(index=False))

if __name__ == '__main__':
    analyze()
