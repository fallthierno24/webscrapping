import pandas as pd
from collections import Counter

def analyze_data(df):
    # Distribution par source
    sources_distribution = df['source'].value_counts().to_dict()
    
    # Top entreprises (si la colonne existe)
    top_companies = {}
    if 'Entreprise' in df.columns:
        top_companies = dict(Counter(df['Entreprise'].dropna()).most_common(5))
    
    # Plage de dates (si la colonne existe)
    date_range = {}
    if 'date_publication' in df.columns:
        dates = pd.to_datetime(df['date_publication'])
        date_range = {
            'start': dates.min().strftime('%Y-%m-%d'),
            'end': dates.max().strftime('%Y-%m-%d')
        }
    
    return {
        'sources_distribution': sources_distribution,
        'top_companies': top_companies,
        'date_range': date_range
    }