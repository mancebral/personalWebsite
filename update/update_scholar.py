import os
import requests
import pandas as pd
import json

API_KEY = os.getenv("SERPAPI_KEY")
SCHOLAR_ID = "Maj9ubYAAAAJ"
BASE_URL = "https://serpapi.com/search.json"


# ======================================================
# 1. DESCARGAR PERFIL COMPLETO
# ======================================================

params_profile = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY
}

profile_data = requests.get(BASE_URL, params=params_profile).json()

# Guardamos JSON bruto para depuración
with open("scholar_raw.json", "w", encoding="utf8") as f:
    json.dump(profile_data, f, ensure_ascii=False, indent=2)

author = profile_data.get("author", {})
cited_by = profile_data.get("cited_by", {})

# -------- Intereses --------
interests = " | ".join(
    i.get("title", "") for i in author.get("interests", []) if isinstance(i, dict)
)

# -------- Métricas completas --------
h_index = None
h_index_5y = None
i10_index = None
i10_index_5y = None
citations_total = None

table = cited_by.get("table", [])

for row in table:
    if "citations" in row:
        citations_total = row["citations"].get("all")
    if "h_index" in row:
        h_index = row["h_index"].get("all")
        h_index_5y = row["h_index"].get("since_2019")
    if "i10_index" in row:
        i10_index = row["i10_index"].get("all")
        i10_index_5y = row["i10_index"].get("since_2019")

# -------- Citas por año --------
citations_year = cited_by.get("graph", [])  # lista de dicts


# -------- Crear dataframe del perfil --------
df_profile = pd.DataFrame([{
    "name": author.get("name", ""),
    "affiliation": author.get("affiliations", ""),
    "interests": interests,
    "citations_total": citations_total,
    "h_index": h_index,
    "h_index_5y": h_index_5y,
    "i10_index": i10_index,
    "i10_index_5y": i10_index_5y
}])

df_profile.to_csv("scholar_profile.csv", index=False)
print("Perfil guardado → scholar_profile.csv")


# ======================================================
# 2. DESCARGAR TODAS LAS PUBLICACIONES (PAGINADAS)
# ======================================================

all_articles = []

next_url = (
    f"{BASE_URL}?engine=google_scholar_author&author_id={SCHOLAR_ID}&api_key={API_KEY}"
)

while next_url:
    data = requests.get(next_url).json()

    articles = data.get("articles", [])
    all_articles.extend(articles)

    # siguiente página
    next_url = data.get("serpapi_pagination", {}).get("next")

# procesar artículos
clean_articles = []
for a in all_articles:
    authors = a.get("authors", [])
    if isinstance(authors, list):
        authors = ", ".join(authors)

    cited_value = (
        a.get("cited_by", {}).get("value")
        if isinstance(a.get("cited_by"), dict)
        else None
    )

    clean_articles.append({
        "title": a.get("title"),
        "year": a.get("year"),
        "authors": authors,
        "journal": a.get("publication"),
        "cited_by": cited_value,
        "scholar_link": a.get("link"),
        "pdf": a.get("pdf")
    })

df_articles = pd.DataFrame(clean_articles)
df_articles.to_csv("scholar.csv", index=False)
print(f"Artículos guardados → scholar.csv ({len(df_articles)} artículos)")


# ======================================================
# 3. PUBLICACIONES POR AÑO + CITAS POR AÑO
# ======================================================

# --- publicaciones por año ---
pubs_by_year = (
    df_articles.dropna(subset=["year"])
    .groupby("year")
    .size()
    .reset_index(name="publications")
)

# --- citas por año ---
cit_year_df = pd.DataFrame(citations_year)

cit_year_df.columns = ["year", "citations"]
cit_year_df["year"] = cit_year_df["year"].astype(int)

# fusionamos
df_stats = pd.merge(
    cit_year_df,
    pubs_by_year,
    on="year",
    how="outer"
).sort_values("year")

df_stats.to_csv("scholar_stats.csv", index=False)

print("Estadísticas guardadas → scholar_stats.csv")


