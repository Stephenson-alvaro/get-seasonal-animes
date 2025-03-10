import requests
import time
import json

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
        all_anime.extend(data['data'])

        if not data['pagination']['has_next_page']:
            break

        page += 1
        time.sleep(1)  # Respect des limites de l'API

    return all_anime

def extract_anime_info(anime):
    """Extrait uniquement les informations souhaitées pour un anime donné."""
    aired = anime.get("aired", {})
    return {
        "mal_id": anime.get("mal_id"),
        "title": anime.get("title"),
        "cover_src": anime.get("images", {}).get("jpg", {}).get("large_image_url"),
        "anime_type": anime.get("type", "Unknown"),
        "episodes": anime.get("episodes", 0),
        "status": anime.get("status", "Unknown"),
        "aired_from": aired.get("from"),
        "aired_to": aired.get("to"),
        "score": anime.get("score", 0.0),
        "synopsis": anime.get("synopsis"),
        "studios": ", ".join(s["name"] for s in anime.get("studios", [])),
        "genres": ", ".join(g["name"] for g in anime.get("genres", [])),
        "themes": ", ".join(t["name"] for t in anime.get("themes", []))
    }

# Récupération des données de chaque saison
current_season = fetch_season_anime('now')
upcoming_season = fetch_season_anime('upcoming')

# Traitement des données pour n'extraire que les informations souhaitées
current_season_processed = [extract_anime_info(anime) for anime in current_season]
upcoming_season_processed = [extract_anime_info(anime) for anime in upcoming_season]

# Création de la structure de données finale
anime_data = {
    "now": current_season_processed,
    "upcoming": upcoming_season_processed
}

# Sauvegarde en JSON
with open('seasonal_animes.json', 'w', encoding='utf-8') as f:
    json.dump(anime_data, f, ensure_ascii=False, indent=4)

print("Données sauvegardées dans anime_seseasonal_animesasons.json")
  
