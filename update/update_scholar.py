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

import json

print("\n=== PROFILE_DATA ===")
print(json.dumps(profile_data, indent=2, ensure_ascii=False))

print("\n=== PROFILE ===")
print(json.dumps(profile, indent=2, ensure_ascii=False))

print("\n=== CITED_BY ===")
print(json.dumps(cited_by, indent=2, ensure_ascii=False))


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
def clean_value(v):
    if isinstance(v, dict):
        return str(v)
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    if v is None:
        return ""
    return v

# ---- MÉTRICAS (h_index, i10_index, citations) ----
stats = profile.get("cited_by", {})

h_index = None
h_index_5y = None
i10_index = None
i10_index_5y = None
cited_by = None

if isinstance(stats, dict):
    table = stats.get("table", [])

    # Example table format:
    # [
    #   {"citations": {"all": 736, "since_2019": 652}},
    #   {"h_index": {"all": 15, "since_2019": 14}},
    #   {"i10_index": {"all": 18, "since_2019": 17}}
    # ]

    for row in table:
        if "citations" in row:
            cited_by = row["citations"].get("all")
        if "h_index" in row:
            h_index = row["h_index"].get("all")
            h_index_5y = row["h_index"].get("since_2019")
        if "i10_index" in row:
            i10_index = row["i10_index"].get("all")
            i10_index_5y = row["i10_index"].get("since_2019")

df_profile = pd.DataFrame([{
    "name": clean_value(profile.get("name", "")),
    "affiliation": clean_value(profile.get("affiliation", "")),
    "interests": clean_value(interests),
    "h_index": clean_value(h_index),
    "h_index_5y": clean_value(h_index_5y),
    "i10_index": clean_value(i10_index),
    "i10_index_5y": clean_value(i10_index_5y),
    "cited_by": clean_value(cited_by)
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

