from flask import Flask, render_template, request
import pandas as pd
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend non interactif
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
from collections import Counter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

def load_data():
    # Remplacez par votre propre chargement de données
    df = pd.read_csv("classified_data.csv")
    return df

def analyze_data(df, source_filter=None):
    # Filtrer les données si un filtre de source est appliqué
    if source_filter:
        df = df[df['source'] == source_filter]
    
    # Initialiser le dictionnaire d'analyse
    analysis = {
        'job_count': len(df),
        'sources_distribution': {},
        'top_companies': {},
        'date_range': None
    }
    
    # Distribution par source (seulement si pas de filtre)
    if not source_filter and 'source' in df.columns:
        analysis['sources_distribution'] = df['source'].value_counts().to_dict()
    
    # Top entreprises
    if 'Entreprise' in df.columns:
        analysis['top_companies'] = dict(Counter(df['Entreprise'].dropna()).most_common(5))
    
    # Plage de dates pour senjob
    if not source_filter or source_filter == 'senjob':
        if 'date_publication' in df.columns and 'source' in df.columns:
            senjob_dates = df[df['source'] == 'senjob']['date_publication'].dropna()
            if not senjob_dates.empty:
                dates = pd.to_datetime(senjob_dates)
                analysis['date_range'] = {
                    'start': dates.min().strftime('%Y-%m-%d'),
                    'end': dates.max().strftime('%Y-%m-%d')
                }
    
    return analysis

def generate_wordcloud(text_series):
    plt.switch_backend('Agg')  # Spécifier le backend non interactif
    
    if text_series.empty or not all(isinstance(x, str) for x in text_series.dropna()):
        # Retourner une image vide ou un placeholder si pas de texte
        img = BytesIO()
        plt.figure(figsize=(12, 8))
        plt.text(0.5, 0.5, 'No text data available', ha='center', va='center')
        plt.axis('off')
        plt.savefig(img, format='png', bbox_inches='tight', dpi=300)
        plt.close()
    else:
        text = ' '.join(text_series.dropna())
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        img = BytesIO()
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=300)
        plt.close()
    
    img.seek(0)
    img_data = base64.b64encode(img.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_data}"

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    df = load_data()
    
    # Préparer la liste des sources
    sources = ['Toutes']
    if 'source' in df.columns:
        sources += sorted(df['source'].unique().tolist())
    
    selected_source = request.form.get('source_filter', 'Toutes')
    
    # Filtrer les données si nécessaire
    if selected_source != 'Toutes':
        df = df[df['source'] == selected_source]
    
    # Analyser les données
    analysis = analyze_data(df)
    
    # Préparer les données pour le wordcloud
    text_column = 'titres' if 'titres' in df.columns else df.columns[0]
    wordcloud_img = generate_wordcloud(df[text_column])
    # Préparer les offres pour le tableau
    offres = df.to_dict('records')
    context = {
        'wordcloud': wordcloud_img,
        'job_count': analysis['job_count'],
        'sources_distribution': analysis['sources_distribution'],
        'top_companies': analysis['top_companies'],
        'date_range': analysis['date_range'],
        'sources': sources,
        'selected_source': selected_source,
        'offres': offres,  # Ajout des offres
        'show_dates': 'date_publication' in df.columns  # Pour afficher/masquer la colonne date
    }
    
    return render_template('index.html', **context)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)