import os
import requests
import pandas as pd
import json

API_KEY = os.getenv("SERPAPI_KEY")
SCHOLAR_ID = "Maj9ubYAAAAJ"

BASE_URL = "https://serpapi.com/search.json"


#########################################################
# 1. DESCARGAR PERFIL COMPLETO Y GUARDAR JSON RAW
#########################################################

params_profile = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY
}

r_profile = requests.get(BASE_URL, params=params_profile)
profile_data = r_profile.json()

# Guardar JSON para inspección
with open("scholar_raw.json", "w", encoding="utf8") as f:
    json.dump(profile_data, f, ensure_ascii=False, indent=2)

print("JSON RAW guardado → scholar_raw.json")

#########################################################
# 2. EXTRAER DATOS DEL PERFIL
#########################################################

author = profile_data.get("author", {})
cited_by = profile_data.get("cited_by", {})

# ---- Interests ----
interests_raw = author.get("interests", [])
interests = " | ".join(
    i.get("title", "") if isinstance(i, dict) else str(i)
    for i in interests_raw
)

# ---- Inicializar métricas ----
citations_total = None
citations_5y = None
h_index = None
h_index_5y = None
i10_index = None
i10_index_5y = None

table = cited_by.get("table", [])

for row in table:
    if "citations" in row:
        citations_total = row["citations"].get("all")
        citations_5y = row["citations"].get("since_2020") or row["citations"].get("since_2019")
    if "h_index" in row:
        h_index = row["h_index"].get("all")
        h_index_5y = row["h_index"].get("since_2020") or row["h_index"].get("since_2019")
    if "i10_index" in row:
        i10_index = row["i10_index"].get("all")
        i10_index_5y = row["i10_index"].get("since_2020") or row["i10_index"].get("since_2019")

# ---- Crear dataframe del perfil ----
df_profile = pd.DataFrame([{
    "name": author.get("name", ""),
    "affiliation": author.get("affiliations", ""),
    "interests": interests,
    "citations_total": citations_total,
    "citations_5y": citations_5y,
    "h_index": h_index,
    "h_index_5y": h_index_5y,
    "i10_index": i10_index,
    "i10_index_5y": i10_index_5y
}])

df_profile.to_csv("scholar_profile.csv", index=False)
print("Perfil guardado → scholar_profile.csv")


#########################################################
# 3. DESCARGAR TODAS LAS PUBLICACIONES (PAGINACIÓN)
#########################################################

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
            "year": a.get("year"),
            "authors": ", ".join(a.get("authors", [])) if isinstance(a.get("authors"), list) else None,
            "journal": a.get("publication"),
            "cited_by": a.get("cited_by", {}).get("value") if isinstance(a.get("cited_by"), dict) else None,
            "scholar_link": a.get("link"),
            "pdf": a.get("pdf")
        }

        all_articles.append(entry)

    start += 20

df_articles = pd.DataFrame(all_articles)
df_articles.to_csv("scholar.csv", index=False)
print(f"Artículos guardados → scholar.csv ({len(df_articles)} artículos)")


#########################################################
# 4. TABLAS EXTRA: PUBLICACIONES POR AÑO Y CITAS POR AÑO
#########################################################

# --- Publicaciones por año ---
pubs_by_year = (
    df_articles.dropna(subset=["year"])
               .assign(year=lambda x: pd.to_numeric(x["year"], errors="coerce"))
               .dropna(subset=["year"])
               .astype({"year": int})
               .groupby("year")
               .size()
               .reset_index(name="n")
               .sort_values("year")
)

# --- Citas por año ---
citations_graph = cited_by.get("graph", [])
citations_year = pd.DataFrame(citations_graph)

if "year" in citations_year.columns:
    citations_year["year"] = pd.to_numeric(citations_year["year"], errors="coerce")
    citations_year = citations_year.dropna(subset=["year"]).astype({"year": int})

# --- Guardar stats ---
df_stats = pd.merge(
    pubs_by_year,
    citations_year,
    on="year",
    how="outer"
).sort_values("year")

df_stats.to_csv("scholar_stats.csv", index=False)

print("Stats guardadas → scholar_stats.csv")
print(df_stats)


