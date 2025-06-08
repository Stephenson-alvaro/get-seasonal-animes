import requests
import time
import json
import asyncio
from googletrans import Translator

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

def remove_duplicates_by_id_and_title(anime_list):
    """Élimine les doublons basés sur mal_id et title."""
    seen = set()
    unique_anime = []
    for anime in anime_list:
        identifier = (anime.get("mal_id"), anime.get("title"))
        if identifier not in seen:
            seen.add(identifier)
            unique_anime.append(anime)
    return unique_anime

async def translate_text(text):
    """Traduit un texte donné en français."""
    translator = Translator()
    if text:
        try:
            async with Translator() as translator:
                result = await translator.translate(text, src='en', dest='fr')
                return result.text

        except Exception as e:
            print("Erreur de connexion :", e)
            return text
    return ""

def extract_anime_info(anime):
    """Extrait uniquement les informations souhaitées pour un anime donné."""
    synopsis = anime.get("synopsis", "")
    translated_synopsis = asyncio.run(translate_text(synopsis))  # Traduction du synopsis
    
    return {
        "mal_id": anime.get("mal_id"),
        "title": anime.get("title"),
        "cover_src": anime.get("images", {}).get("jpg", {}).get("large_image_url"),
        "anime_type": anime.get("type", "Unknown"),
        "episodes": anime.get("episodes", 0),
        "status": anime.get("status", "Unknown"),
        "score": anime.get("score", 0.0),
        "synopsis": translated_synopsis,
        "studios": ", ".join(s["name"] for s in anime.get("studios", [])),
        "genres": ", ".join(g["name"] for g in anime.get("genres", [])),
        "themes": ", ".join(t["name"] for t in anime.get("themes", []))
    }

# Récupération et fusion des deux saisons
current_season = fetch_season_anime('now')
upcoming_season = fetch_season_anime('upcoming')

# Fusion et suppression des doublons
all_anime_raw = current_season + upcoming_season
unique_anime_raw = remove_duplicates_by_id_and_title(all_anime_raw)

# Traitement
anime_processed = [extract_anime_info(anime) for anime in unique_anime_raw]

# Sauvegarde JSON
with open('seasonal_animes.json', 'w', encoding='utf-8') as f:
    json.dump(anime_processed, f, ensure_ascii=False, indent=4)

print("Données sauvegardées dans seasonal_animes.json")
