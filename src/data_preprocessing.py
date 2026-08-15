import pandas as pd
from sklearn.preprocessing import StandardScaler

class DataPreprocessor:
    def __init__(self, file_path: str, min_overall: int = 70):
        self.file_path = file_path
        self.min_overall = min_overall
        #  oyuncu profillerini netleştiren 6 Temel Kart Statüsü
        self.skills = [
            'pace', 
            'shooting', 
            'passing', 
            'dribbling', 
            'defending', 
            'physic'
        ]
        self.scaler = StandardScaler()

    def process(self):
        df = pd.read_csv(self.file_path, low_memory=False)

        # 1. Kalecileri filtreleme (Sadece saha içi oyuncuları alma)
        pos_col = 'player_positions' if 'player_positions' in df.columns else 'club_position'
        df_field = df[~df[pos_col].astype(str).str.contains('GK', na=False)].copy()

        # 2. Overall reyting filtresi (Kaliteli ve bilinen oyuncu havuzu için 70+)
        overall_col = 'overall' if 'overall' in df.columns else 'Overall'
        df_field = df_field[df_field[overall_col] >= self.min_overall].copy()

        # 3. Mükerrer ve Sahte Oyuncu Filtresi
        name_col = 'short_name' if 'short_name' in df_field.columns else 'Name'
        
        # Lisanssız/Sahte EA verilerini temizleme
        if 'league_name' in df_field.columns:
            df_field = df_field[df_field['league_name'] != 'Rep. Ireland Premier Division']

        # Oyuncuları reytinge göre sıralayıp isim bazında tekilleştirme
        df_field = df_field.sort_values(overall_col, ascending=False).drop_duplicates(subset=[name_col]).copy()

        # 4. Yeteneklerin seçilmesi ve eksik verilerin ortalama ile doldurulması
        valid_skills = [c for c in self.skills if c in df_field.columns]
        X = df_field[valid_skills].fillna(df_field[valid_skills].mean())

        # 5. Standardizasyon (Z-Score ölçekleme)
        X_scaled = self.scaler.fit_transform(X)

        return df_field, X_scaled, valid_skills