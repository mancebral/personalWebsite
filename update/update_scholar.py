import os
import requests
import pandas as pd

API_KEY = os.getenv("SERPAPI_KEY")
SCHOLAR_ID = "Maj9ubYAAAAJ&hl"

BASE_URL = "https://serpapi.com/search.json"


# ============================================
# 1. DESCARGAR PERFIL DEL AUTOR
# ============================================

params_profile = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY
}

r_profile = requests.get(BASE_URL, params=params_profile)
profile_data = r_profile.json().get("author", {})

profile = {
    "name": profile_data.get("name"),
    "affiliation": profile_data.get("affiliations"),
    "email": profile_data.get("email"),
    "description": profile_data.get("description"),
    "interests": ", ".join([i.get("title", "") for i in profile_data.get("interests", [])]),
    "thumbnail": profile_data.get("thumbnail")
}

pd.DataFrame([profile]).to_csv("scholar_profile.csv", index=False)
print("scholar_profile.csv generado correctamente.")


# ============================================
# 2. DESCARGAR TODAS LAS PUBLICACIONES (paginando)
# ============================================

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

        # --- JOURNAL ---
        a["journal"] = a.get("publication")

        # --- LINK SCHOLAR ---
        a["scholar_link"] = a.get("link")

        # --- LINK PDF ---
        a["pdf"] = a.get("pdf")

    all_articles.extend(articles)
    start += 20


# Convertir a DataFrame
df = pd.DataFrame(all_articles)

# columnas ordenadas
cols = [
    "title", "year", "authors", "journal",
    "cited_by", "scholar_link", "pdf"
]

df = df[[c for c in cols if c in df.columns]]

# Guardar CSV final
df.to_csv("scholar.csv", index=False)

print(f"scholar.csv generado con {len(df)} artículos.")

