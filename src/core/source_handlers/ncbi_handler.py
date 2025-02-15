from .base_handler import BaseSourceHandler
import requests
import xml.etree.ElementTree as ET

class NCBIHandler(BaseSourceHandler):
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def search_articles(self, query: str, max_results: int = 10):
        try:
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {
                "db": "pmc",
                "term": query,
                "retmode": "json",
                "retmax": max_results
            }
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pmc_ids = data.get("esearchresult", {}).get("idlist", [])
            return pmc_ids
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching search results: {e}")
            return []

    def get_article_metadata(self, article_ids: list):
        try:
            summary_url = f"{self.base_url}/esummary.fcgi"
            summary_params = {
                "db": "pmc",
                "id": ",".join(article_ids),
                "retmode": "json"
            }
            response = requests.get(summary_url, params=summary_params, timeout=10)
            response.raise_for_status()
            summary_data = response.json()
            
            article_info = {}
            for pmc_id in article_ids:
                doc = summary_data.get("result", {}).get(pmc_id, {})
                title = doc.get("title", "Title Not Available")
                article_info[pmc_id] = {"title": title, "links": []}
            return article_info
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching article metadata: {e}")
            return {}

    def get_supplementary_materials(self, article_ids: list):
        article_info = self.get_article_metadata(article_ids)
        fetch_url = f"{self.base_url}/efetch.fcgi"

        for pmc_id in article_ids:
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

            except (requests.exceptions.RequestException, ET.ParseError) as e:
                print(f"⚠️ Error processing PMC{pmc_id}: {e}")

        return article_info
