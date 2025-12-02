import os
import requests
import pandas as pd

API_KEY = os.getenv("SERPAPI_KEY")
SCHOLAR_ID = "Maj9ubYAAAAJ&hl"

BASE_URL = "https://serpapi.com/search.json"

########################################
# 1. DESCARGAR PERFIL (h-index, i10, citas/año)
########################################

params_profile = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY
}

r_profile = requests.get(BASE_URL, params=params_profile)
profile_data = r_profile.json()

profile = profile_data.get("author", {})
cited_by = profile_data.get("cited_by", {})

# ---- h-index, i10, citations ----
metrics = {}
if "table" in cited_by:
    for row in cited_by["table"]:
        name = row.get("name")
        if name == "Citations":
            metrics["citations_all"] = row.get("all")
            metrics["citations_recent"] = row.get("since_2019")
        if name == "h-index":
            metrics["h_index_all"] = row.get("all")
            metrics["h_index_recent"] = row.get("since_2019")
        if name == "i10-index":
            metrics["i10_all"] = row.get("all")
            metrics["i10_recent"] = row.get("since_2019")

# ---- citas por año ----
citations_per_year = cited_by.get("graph", {})

# ---- intereses en formato "A | B | C" ----
interests_list = profile.get("interests", [])

if isinstance(interests_list, list):
    interests = " | ".join(
        i["title"] if isinstance(i, dict) and "title" in i else str(i)
        for i in interests_list
    )
else:
    interests = ""

# ---- crear dataframe del perfil ----
df_profile = pd.DataFrame([{
    "name": profile.get("name"),
    "affiliation": profile.get("affiliations"),
    "email": profile.get("email"),
    "interests": interests,
    **metrics,
    **citations_per_year
}])

df_profile.to_csv("scholar_profile.csv", index=False)

print("Perfil descargado con éxito.")

########################################
# 2. DESCARGAR PUBLICACIONES (tu código)
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

        if isinstance(a.get("cited_by"), dict):
            a["cited_by"] = a["cited_by"]["value"]
        else:
            a["cited_by"] = None

        if isinstance(a.get("authors"), list):
            a["authors"] = ", ".join(a["authors"])

        a["journal"] = a.get("publication")
        a["scholar_link"] = a.get("link")
        a["pdf"] = a.get("pdf")

    all_articles.extend(articles)
    start += 20

df = pd.DataFrame(all_articles)

cols = [
    "title", "year", "authors", "journal",
    "cited_by", "scholar_link", "pdf"
]

df = df[[c for c in cols if c in df.columns]]
df.to_csv("scholar.csv", index=False)

print(f"CSV generado con {len(df)} artículos.")

