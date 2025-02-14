import requests
import xml.etree.ElementTree as ET

# Step 1: Search for articles based on user input
def search_articles(query, max_results=10):
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pmc",
            "term": f"{query} open access[filter]",
            "retmode": "json",
            "retmax": max_results
        }

        response = requests.get(search_url, params=search_params, timeout=10)
        response.raise_for_status()
        data = response.json()

        pmc_ids = data.get("esearchresult", {}).get("idlist", [])
        if not pmc_ids:
            print("❌ No articles found.")
            return []
        return pmc_ids

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching search results: {e}")
        return []


# Step 2: Fetch article metadata (title) using ESummary
def get_article_titles(pmc_ids):
    try:
        if not pmc_ids:
            return {}

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "pmc",
            "id": ",".join(pmc_ids),
            "retmode": "json"
        }

        response = requests.get(summary_url, params=summary_params, timeout=10)
        response.raise_for_status()
        summary_data = response.json()

        article_info = {}
        for pmc_id in pmc_ids:
            doc = summary_data.get("result", {}).get(pmc_id, {})
            title = doc.get("title", "Title Not Available")
            article_info[pmc_id] = {"title": title, "links": []}
        return article_info

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching article titles: {e}")
        return {}


# Step 3: Fetch full article XML and extract supplementary material links
def get_supplementary_links(pmc_ids, article_info):
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    for pmc_id in pmc_ids:
        try:
            fetch_params = {"db": "pmc", "id": pmc_id, "retmode": "xml"}
            response = requests.get(fetch_url, params=fetch_params, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            links = []

            for supp_mat in root.findall(".//supplementary-material"):
                link = supp_mat.get("{http://www.w3.org/1999/xlink}href")
                if link:
                    links.append(link)

            if links:
                article_info[pmc_id]["links"] = links

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching article PMC{pmc_id}: {e}")
        except ET.ParseError:
            print(f"⚠️ Error parsing XML for PMC{pmc_id}")

    return article_info


# Step 4: Display results
def display_results(article_info):
    found_supplements = False
    for pmc_id, info in article_info.items():
        if info["links"]:
            found_supplements = True
            print(f"📝 **{info['title']}** (PMC{pmc_id})")
            for link in info["links"]:
                print(f"   📎 {link}")
            print("\n" + "-" * 60)

    if not found_supplements:
        print("❌ No supplementary materials found for the retrieved articles.")


# 🔥 Main Execution Flow
if __name__ == "__main__":
    search_query = input("🔍 Enter search phrase (e.g., 'brain MRI'): ").strip()
    if not search_query:
        print("⚠️ Search phrase cannot be empty!")
    else:
        pmc_ids = search_articles(search_query)
        article_info = get_article_titles(pmc_ids)
        article_info = get_supplementary_links(pmc_ids, article_info)
        display_results(article_info)
