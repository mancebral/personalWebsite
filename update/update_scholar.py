from scholarly import scholarly
import csv

# Cambia esto por TU Google Scholar ID
# El ID es lo que aparece en la URL después de user=
SCHOLAR_ID = "Maj9ubYAAAAJ&hl"

author = scholarly.search_author_id(SCHOLAR_ID)
author = scholarly.fill(author)

# Guardamos publicaciones en un CSV
with open("scholar.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "year", "cited_by"])

    for pub in author["publications"]:
        pub_filled = scholarly.fill(pub)
        title = pub_filled.get("bib", {}).get("title", "")
        year = pub_filled.get("bib", {}).get("pub_year", "")
        cites = pub_filled.get("num_citations", 0)

        writer.writerow([title, year, cites])


