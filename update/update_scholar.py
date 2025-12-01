#SCHOLAR_ID = "Maj9ubYAAAAJ&hl"
import os
import json
import pandas as pd
import requests

API_KEY = os.getenv("SERPAPI_KEY")  # viene desde GitHub Secrets
SCHOLAR_ID = "Maj9ubYAAAAJ&hl"     # sustituye

url = "https://serpapi.com/search.json"

params = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY
}

r = requests.get(url, params=params)
data = r.json()

# extraer publicaciones
pubs = data.get("articles", [])

df = pd.DataFrame(pubs)
df.to_csv("scholar.csv", index=False)

print("Archivo scholar.csv actualizado.")



