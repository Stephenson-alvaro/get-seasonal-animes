import requests
import time
import json
import base64
from io import BytesIO

def fetch_season_anime(season_type):
    """Récupère tous les animés d'une saison donnée (now/upcoming)"""
    all_anime = []
    page = 1
    
    while True:
        url = f"https://api.jikan.moe/v4/seasons/{season_type}?page={page}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Erreur {response.status_code} sur la page {page} ({season_type})")
            break
            
        data = response.json()
        
        for anime in data['data']:
            if 'images' in anime and 'jpg' in anime['images']:
                image_url = anime['images']['jpg']['large_image_url']
                anime['images']['jpg']['large_image_base64'] = image_to_base64(image_url)
            
        all_anime.extend(data['data'])
        
        # Vérification s'il y a une page suivante
        if not data['pagination']['has_next_page']:
            break
            
        page += 1
        time.sleep(1)  # Respect des limites de l'API
    
    return all_anime

def image_to_base64(image_url):
    """Télécharge une image et la convertit en base64"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        else:
            print(f"Erreur lors du téléchargement de l'image : {image_url}")
            return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None

# Récupération des données
current_season = fetch_season_anime('now')
upcoming_season = fetch_season_anime('upcoming')

# Création de la structure de données
anime_data = {
    "now": current_season,
    "upcoming": upcoming_season
}

# Sauvegarde en JSON
with open('anime_seasons.json', 'w', encoding='utf-8') as f:
    json.dump(anime_data, f, ensure_ascii=False, indent=4)

print("Données sauvegardées dans anime_seasons.json")
