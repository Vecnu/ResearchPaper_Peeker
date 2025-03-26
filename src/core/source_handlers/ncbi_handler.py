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
                        
                        # Find all supplementary material nodes
                        supp_materials = article.findall(".//supplementary-material")
                        
                        for supp in supp_materials:
                            # Look for media elements with xlink:href attributes
                            media_elements = supp.findall(".//media")
                            for media in media_elements:
                                href = media.get("{http://www.w3.org/1999/xlink}href")
                                if href:
                                    # Construct the full URL for downloading
                                    full_download_url = f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{pmc_id}/bin/{href}"
                                    supp_links.append(full_download_url)
                                    print(f"Found supplementary material: {full_download_url}")
                        
                        if supp_links:
                            all_materials[pmc_id] = supp_links
                            print(f"  Article PMC{pmc_id}: Found {len(supp_links)} supplementary materials")
                            
                        # Add a sleep between batches
                        if i < len(article_ids) - batch_size:
                            time.sleep(1)
                            
                return all_materials
        except requests.exceptions.RequestException as e:
            print(f"Error fetching supplementary materials: {e}")
            return {}
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
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

def save_efetch_xml_responses(self, article_ids, output_dir=None):
    """
    Fetch XML responses for given PMC IDs using efetch and save them to files.
    This method is for testing/debugging purposes only.
    
    Args:
        article_ids: List of PMC IDs
        output_dir: Directory to save XML files (optional)
        
    Returns:
        List of paths to saved XML files
    """
    import os
    from pathlib import Path
    import datetime
    
    saved_files = []
    
    # Create output directory for XML responses
    if output_dir is None:
        # Create a folder with today's date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        base_dir = Path("output")
        output_dir = base_dir / today / "xml_responses"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created XML output directory: {output_dir}")
    else:
        output_dir = Path(output_dir) / "xml_responses"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Using provided XML output directory: {output_dir}")
    
    # Process in batches of 10 to avoid overwhelming the API
    batch_size = 10
    for i in range(0, len(article_ids), batch_size):
        batch_ids = article_ids[i:i+batch_size]
        batch_number = i // batch_size + 1
        
        try:
            # Use efetch to get full article XML
            efetch_url = f"{self.base_url}/efetch.fcgi"
            efetch_params = {
                "db": "pmc",
                "id": ",".join(batch_ids),
                "retmode": "xml"
            }
            
            # For debugging
            full_url = requests.Request('GET', efetch_url, params=efetch_params).prepare().url
            print(f"EFetch URL (Batch {batch_number}): {full_url}")
            
            response = requests.get(efetch_url, params=efetch_params, timeout=30)
            response.raise_for_status()
            
            # Create a meaningful filename
            batch_file_name = f"batch_{batch_number}_ids_{'-'.join(batch_ids)}.xml"
            xml_file_path = output_dir / batch_file_name
            
            # Save the raw XML response
            with open(xml_file_path, 'wb') as xml_file:
                xml_file.write(response.content)
            
            saved_files.append(str(xml_file_path))
            print(f"✅ Saved XML response for batch {batch_number} to {xml_file_path}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching XML for batch {batch_number}: {e}")
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error saving XML for batch {batch_number}: {e}")
            continue
    
    print(f"Total XML files saved: {len(saved_files)}")
    return saved_files
