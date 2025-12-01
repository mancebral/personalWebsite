#SCHOLAR_ID = "Maj9ubYAAAAJ&hl"
import os
import requests
import pandas as pd

API_KEY = os.getenv("SERPAPI_KEY")     # desde GitHub Secrets
SCHOLAR_ID = "Maj9ubYAAAAJ&hl"        # -> cámbialo por el tuyo

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
        break  # no hay más páginas

    all_articles.extend(articles)
    start += 20  # siguiente página

df = pd.DataFrame(all_articles)
df.to_csv("scholar.csv", index=False)

print(f"Descargados {len(all_articles)} artículos.")
