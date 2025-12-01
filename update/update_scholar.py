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

    for a in articles:

        # --- CITES ---
        if isinstance(a.get("cited_by"), dict):
            a["cited_by"] = a["cited_by"]["value"]
        else:
            a["cited_by"] = None

        # --- AUTORES ---
        if isinstance(a.get("authors"), list):
            a["authors"] = ", ".join(a["authors"])

        # --- JOURNAL / PUBLICATION ---
        a["journal"] = a.get("publication")

        # --- LINK A SCHOLAR ---
        a["scholar_link"] = a.get("link")

        # --- LINK DIRECTO A PDF (si existe) ---
        a["pdf"] = a.get("pdf")

    all_articles.extend(articles)
    start += 20

df = pd.DataFrame(all_articles)

# columnas recomendadas
cols = [
    "title", "year", "authors", "journal",
    "cited_by", "scholar_link", "pdf"
]

df = df[[c for c in cols if c in df.columns]]

df.to_csv("scholar.csv", index=False)

print(f"CSV generado con {len(df)} artículos.")
