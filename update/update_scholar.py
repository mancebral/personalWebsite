#SCHOLAR_ID = "Maj9ubYAAAAJ&hl"
import os
import requests
import pandas as pd

API_KEY = os.getenv("SERPAPI_KEY")
SCHOLAR_ID = "Maj9ubYAAAAJ&hl"

BASE_URL = "https://serpapi.com/search.json"

all_articles = []
start = 0

while True:
    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key": API_KEY,
        "start": start
    }

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    articles = data.get("articles", [])
    if not articles:
        break

    # --- LIMPIAR DATOS ---
    for a in articles:
        # Cites: convertir dict -> número
        if isinstance(a.get("cited_by"), dict):
            a["cited_by_value"] = a["cited_by"].get("value")
        else:
            a["cited_by_value"] = None

        # También puedes limpiar autores (lista -> string)
        if isinstance(a.get("authors"), list):
            a["authors"] = ", ".join(a["authors"])

    all_articles.extend(articles)
    start += 20

df = pd.DataFrame(all_articles)

# Si quieres SOLO columnas limpias:
cols = ["title", "year", "authors", "cited_by_value", "link"]
df = df[ [c for c in cols if c in df.columns] ]

df.to_csv("scholar.csv", index=False)

print(f"CSV generado con {len(df)} artículos.")
