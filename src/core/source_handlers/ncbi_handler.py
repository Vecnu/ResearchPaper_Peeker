from .base_handler import BaseSourceHandler
import requests
import xml.etree.ElementTree as ET
import time  # Add this import
class NCBIHandler(BaseSourceHandler):
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def search_articles(self, query: str, max_results: int = 100):
        try:
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {
                "db": "pmc",
                "term": f'"{query}" AND "supplementary material"',
                "retmode": "json",
                "retmax": max_results
            }
            full_url = requests.Request('GET', search_url, params=search_params).prepare().url
            print(f"\nSearch Query URL: {full_url}")
            
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
            full_url = requests.Request('GET', summary_url, params=summary_params).prepare().url
            print(f"Metadata Query URL: {full_url}")
            
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
        try:
            fetch_url = f"{self.base_url}/efetch.fcgi"
            batch_size = 9  # Changed from 20 to 10
            all_materials = {}
            total_processed = 0

            print(f"\nScanning {len(article_ids)} articles for supplementary materials...")
            
            for i in range(0, len(article_ids), batch_size):
                batch_ids = article_ids[i:i + batch_size]
                total_processed += len(batch_ids)
                
                print(f"\nProcessing batch {i//batch_size + 1} ({total_processed}/{len(article_ids)} articles)...")
                
                fetch_params = {
                    "db": "pmc",
                    "id": '%2C'.join(batch_ids),
                    "retmode": "xml"
                }
                full_url = requests.Request('GET', fetch_url, params=fetch_params).prepare().url
                print(f"Fetch Query URL (Batch {i//batch_size + 1}): {full_url}")
                
                if i > 0:
                    time.sleep(1)  # Rate limiting
                    
                response = requests.get(fetch_url, params=fetch_params, timeout=10)
                response.raise_for_status()
                
                # Parse XML for supplementary material links
                root = ET.fromstring(response.content)
                
                # Define and register namespaces
                namespaces = {
                    'xlink': 'http://www.w3.org/1999/xlink'
                }
                ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
                
                for article in root.findall(".//article"):
                    pmc_id = article.find(".//article-id[@pub-id-type='pmc']")
                    if pmc_id is not None:
                        pmc_id = pmc_id.text
                        supp_links = []
                        
                        # 1. Find supplementary material sections
                        for supp in article.findall(".//supplementary-material"):
                            # Use findall with xpath to get the attribute with namespace
                            href = supp.get('{http://www.w3.org/1999/xlink}href')
                            if href and any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']):
                                supp_links.append(href)
                        
                        # 2. Find ext-link elements with supplementary file references
                        for ext_link in article.findall(".//ext-link"):
                            href = ext_link.get('{http://www.w3.org/1999/xlink}href')
                            if href and any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']):
                                supp_links.append(href)
                        
                        # 3. Find media elements with supplementary files
                        for media in article.findall(".//media"):
                            href = media.get('{http://www.w3.org/1999/xlink}href')
                            if href and any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']):
                                # For JMIR articles, construct the full URL
                                if href.startswith('jmir_'):
                                    full_href = f"https://asset.jmir.pub/assets/{href}"
                                    supp_links.append(full_href)
                                else:
                                    # For other journals or if already a full URL
                                    supp_links.append(href)
                        
                        if supp_links:
                            all_materials[pmc_id] = supp_links
                            print(f"Found {len(supp_links)} supplementary files in PMC{pmc_id}")

            print(f"\nCompleted scanning {total_processed} articles")
            print(f"Found supplementary materials in {len(all_materials)} articles")
            
            return all_materials
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching supplementary materials: {e}")
            return {}

def process_search_results(self, query: str, max_results: int = 100):
    # Get article IDs from search
    article_ids = self.search_articles(query, max_results)
    
    if not article_ids:
        print("No articles found.")
        return
        
    # Get article metadata (titles)
    metadata = self.get_article_metadata(article_ids)
    
    # Get supplementary materials
    materials = self.get_supplementary_materials(article_ids)
    
    # Count articles with supplementary materials
    articles_with_supps = len(materials)
    total_articles = len(article_ids)
    
    print(f"\nFound {articles_with_supps} articles with supplementary materials out of {total_articles} total results")
    print("\nArticles with supplementary materials:")
    
    for pmc_id, links in materials.items():
        title = metadata.get(pmc_id, {}).get('title', 'Title Not Available')
        print(f"\nTitle: {title}")
        print(f"PMC ID: {pmc_id}")
        print("Supplementary Links:")
        for link in links:
            print(f"- {link}")
