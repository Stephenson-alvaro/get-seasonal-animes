import requests
import json
import asyncio
from googletrans import Translator
import time

def fetch_season_anime(season_type):
    all_anime, page = [], 1
    while True:
        url = f"https://api.jikan.moe/v4/seasons/{season_type}?page={page}"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Erreur {resp.status_code} pour {season_type} page {page}")
            break
        data = resp.json()
        all_anime += data['data']
        if not data['pagination'].get('has_next_page', False):
            break
        page += 1
        time.sleep(1)
    return all_anime

def remove_duplicates(anime_list):
    seen = set()
    unique = []
    for a in anime_list:
        ident = (a.get("mal_id"), a.get("title"))
        if ident not in seen:
            seen.add(ident)
            unique.append(a)
    return unique

async def extract_info(anime, translator):
    synopsis = anime.get("synopsis") or ""
    res = await translator.translate(synopsis, src="en", dest="fr") if synopsis else None
    text_fr = res.text if res and hasattr(res, "text") else ""
    return {
        "mal_id": anime.get("mal_id"),
        "title": anime.get("title"),
        "cover_src": anime.get("images", {}).get("jpg", {}).get("large_image_url"),
        "score": anime.get("score")
    }

async def process(season_type, translator):
    print(f"📥 Récupération {season_type} …")
    raw = fetch_season_anime(season_type)
    uniq = remove_duplicates(raw)
    tasks = [extract_info(a, translator) for a in uniq]
    return await asyncio.gather(*tasks)

async def main():
    async with Translator() as translator:
        now, upcoming = await asyncio.gather(
            process("now", translator),
            process("upcoming", translator),
        )
    data = {"now": now, "upcoming": upcoming}
    with open("seasonal_animes.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("✅ JSON sauvegardé.")

if __name__ == "__main__":
    asyncio.run(main())

