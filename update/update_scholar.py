import os
import requests
import pandas as pd
import json

API_KEY = os.getenv("SERPAPI_KEY")
SCHOLAR_ID = "Maj9ubYAAAAJ"

BASE_URL = "https://serpapi.com/search.json"


########################################
# 1. DESCARGAR PERFIL COMPLETO
########################################

params_profile = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY
}

r_profile = requests.get(BASE_URL, params=params_profile)
profile_data = r_profile.json()

# Guardar el JSON completo para inspeccionarlo
with open("scholar_raw.json", "w", encoding="utf8") as f:
    json.dump(profile_data, f, ensure_ascii=False, indent=2)


# Guardar JSON bruto para depuración
with open("scholar_raw.json", "w") as f:
    json.dump(profile_data, f, indent=2)


########################################
# 2. EXTRAER DATOS DEL PERFIL
########################################

author = profile_data.get("author", {})
cited_by = profile_data.get("cited_by", {})

# ---- Interests ----
interests_raw = author.get("interests", [])
interests = " | ".join(
    i.get("title", "") if isinstance(i, dict) else str(i)
    for i in interests_raw
)

# ---- Métricas h-index, i10-index ----
h_index = None
i10_index = None
citations_total = None

if "table" in cited_by:
    for row in cited_by["table"]:
        if row.get("name") == "Citations":
            citations_total = row.get("all")
        elif row.get("name") == "h-index":
            h_index = row.get("all")
        elif row.get("name") == "i10-index":
            i10_index = row.get("all")

# ---- Citas por año ----
citations_per_year = cited_by.get("graph", {})

# ---- Crear dataframe del perfil ----
df_profile = pd.DataFrame([{
    "name": author.get("name", ""),
    "affiliation": author.get("affiliations", ""),
    "interests": interests,
    "citations_total": citations_total,
    "h_index": h_index,
    "i10_index": i10_index
}])

df_profile.to_csv("scholar_profile.csv", index=False)
print("Perfil guardado → scholar_profile.csv")


########################################
# 3. DESCARGAR TODAS LAS PUBLICACIONES
########################################

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
        entry = {
            "title": a.get("title", ""),
            "year": a.get("year", ""),
            "authors": ", ".join(a.get("authors", [])) if isinstance(a.get("authors"), list) else "",
            "journal": a.get("publication", ""),
            "cited_by": a.get("cited_by", {}).get("value") if isinstance(a.get("cited_by"), dict) else "",
            "scholar_link": a.get("link", ""),
            "pdf": a.get("pdf", "")
        }

        all_articles.append(entry)

    start += 20

df_articles = pd.DataFrame(all_articles)
df_articles.to_csv("scholar.csv", index=False)
print(f"Artículos guardados → scholar.csv ({len(df_articles)} artículos)")


