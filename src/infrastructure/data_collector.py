import os
import datetime
from pathlib import Path

class DataCollector:
    """
    General-purpose utility for collecting and saving data from various sources
    """
    
    def __init__(self):
        """Initialize with empty tracking lists"""
        self.saved_files = []
        self.current_output_dir = None
    
    def create_date_folder(self, base_dir="output"):
        """Create a folder with today's date as name"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        output_dir = Path(base_dir) / today
        os.makedirs(output_dir, exist_ok=True)
        self.current_output_dir = output_dir
        return output_dir
    
    def save_links_to_file(self, source_id, links, output_dir=None, source_type=None):
        """Save links to a text file"""
        if not links:
            print(f"No links found for ID: {source_id}")
            return None
        
        # Create output directory if needed
        if output_dir is None:
            output_dir = self.create_date_folder()
        
        # Create file name with source type prefix if provided
        prefix = f"{source_type}_" if source_type else ""
        output_file = output_dir / f"{prefix}{source_id}_links.txt"
        
        # Write links to file
        with open(output_file, "w") as f:
            for link in links:
                # Save the full URL as is
                f.write(f"{link}\n")
        
        print(f"Saved {len(links)} links for ID {source_id} to {output_file}")
        
        # Track the saved file
        self.saved_files.append((source_id, str(output_file), len(links)))
        
        return str(output_file)
    
    def batch_save_links(self, article_dict, source_type=None):
        """Save multiple sets of links to files in a batch operation"""
        output_dir = self.create_date_folder()
        
        for article_id, links in article_dict.items():
            if links:
                self.save_links_to_file(article_id, links, output_dir, source_type)
        
        return str(output_dir) if self.saved_files else None
    
    def print_summary(self):
        """Print a summary of all files created during this run"""
        if not self.saved_files:
            print("\n📌 No files were saved in this run.")
            return
        
        print("\n📝 Summary of Saved Files:")
        print(f"📁 Output Directory: {self.current_output_dir}")
        print(f"📊 Total Files Created: {len(self.saved_files)}")
        
        total_links = sum(count for _, _, count in self.saved_files)
        print(f"🔗 Total Links Saved: {total_links}")
        
        # Optional: Print detailed list of files if not too many
        if len(self.saved_files) <= 10:  # Only show details if 10 or fewer files
            print("\nDetailed File List:")
            for source_id, file_path, link_count in self.saved_files:
                print(f"  • {source_id}: {link_count} links - {file_path}")
        
        print(f"\n✅ All data has been successfully saved to: {self.current_output_dir}")
    
    def download_all_documents(self, output_dir=None):
        """
        Download all documents from saved link files
        
        Args:
            output_dir: Directory containing the link files (optional)
        
        Returns:
            Number of successfully downloaded files
        """
        import requests
        import os
        from pathlib import Path
        import time
        from urllib.parse import urlparse
        import logging
        from support.logging_service import Logger
        
        # Get logger instance
        logger = Logger.get_instance()
        
        # Use current output directory if none is specified
        if output_dir is None:
            if self.current_output_dir is None:
                logger.warning("No output directory specified and no current directory set.")
                return 0
            output_dir = self.current_output_dir
        else:
            output_dir = Path(output_dir)
        
        # Create documents folder if it doesn't exist
        documents_dir = output_dir / "documents"
        os.makedirs(documents_dir, exist_ok=True)
        logger.info(f"Documents will be saved to: {documents_dir}")
        print(f"Documents will be saved to: {documents_dir}")
        
        # Find all link files in the output directory
        link_files = list(output_dir.glob("*_links.txt"))
        if not link_files:
            logger.warning(f"No link files found in {output_dir}")
            print(f"No link files found in {output_dir}")
            return 0
        
        logger.info(f"Found {len(link_files)} link files with supplementary materials.")
        print(f"Found {len(link_files)} link files with supplementary materials.")
        
        # Browser-like headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # Statistics
        total_links = 0
        successful_downloads = 0
        failed_downloads = 0
        
        # Process each link file
        for link_file in link_files:
            logger.info(f"Processing links from: {link_file.name}")
            print(f"\nProcessing links from: {link_file.name}")
            
            with open(link_file, 'r') as f:
                links = [line.strip() for line in f if line.strip()]
            
            total_links += len(links)
            logger.info(f"Found {len(links)} links to download.")
            print(f"Found {len(links)} links to download.")
            
            # Download each file
            for i, url in enumerate(links):
                try:
                    # Extract filename from URL
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path)
                    
                    # If filename is not valid or empty, generate one
                    if not filename or len(filename) < 3:
                        filename = f"document_{link_file.stem}_{i+1}.bin"
                    
                    # Create full output path
                    output_path = documents_dir / filename
                    
                    # Skip if file already exists
                    if output_path.exists():
                        logger.info(f"File already exists, skipping: {filename}")
                        print(f"File already exists, skipping: {filename}")
                        successful_downloads += 1
                        continue
                    
                    logger.info(f"Downloading {i+1}/{len(links)}: {filename}...")
                    print(f"Downloading {i+1}/{len(links)}: {filename}...")
                    
                    # Add a referer header using the article's base URL
                    article_id = link_file.stem.split('_')[1] if '_' in link_file.stem else 'unknown'
                    referer = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{article_id}/"
                    current_headers = headers.copy()
                    current_headers['Referer'] = referer
                    
                    # Download the file with browser-like headers
                    session = requests.Session()
                    
                    # First, visit the article page to get cookies
                    session.get(referer, headers=current_headers, timeout=30)
                    
                    # Then download the file
                    response = session.get(url, headers=current_headers, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Check if we got actual content
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type and len(response.content) < 10000:
                        # This might be an error page, not the actual file
                        error_msg = f"Received HTML instead of file data (possible access restriction). Content type: {content_type}"
                        logger.error(error_msg)
                        print(f"❌ {error_msg}")
                        
                        # Save the HTML response for debugging
                        error_html_path = documents_dir / f"error_{filename}.html"
                        with open(error_html_path, 'wb') as error_file:
                            error_file.write(response.content)
                        logger.info(f"Saved error HTML to {error_html_path}")
                        
                        failed_downloads += 1
                        continue
                    
                    # Save the file
                    with open(output_path, 'wb') as out_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            out_file.write(chunk)
                    
                    successful_downloads += 1
                    logger.info(f"Successfully downloaded: {filename}")
                    print(f"✅ Successfully downloaded: {filename}")
                    
                    # Brief pause to avoid overwhelming the server
                    time.sleep(1.5)
                    
                except requests.exceptions.RequestException as e:
                    error_msg = f"Failed to download {url}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    print(f"❌ {error_msg}")
                    failed_downloads += 1
                    
                    # Alternative URL suggestion
                    if "403" in str(e):
                        article_id = link_file.stem.split('_')[1] if '_' in link_file.stem else 'unknown'
                        alt_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{article_id}/"
                        logger.info(f"Try manually downloading from: {alt_url}")
                        print(f"💡 Try manually downloading from: {alt_url}")
                except Exception as e:
                    error_msg = f"Error processing {url}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    print(f"❌ {error_msg}")
                    failed_downloads += 1
        
        # Print summary
        summary = f"\n📊 Download Summary:\n" \
                  f"  Total links processed: {total_links}\n" \
                  f"  Successfully downloaded: {successful_downloads}\n" \
                  f"  Failed downloads: {failed_downloads}"
        
        logger.info(summary)
        print(summary)
        
        if failed_downloads > 0:
            alternative_msg = (
                "\nℹ️ Some downloads failed. NCBI may require authentication or browser cookies.\n"
                "Consider manual download by visiting the article pages directly.\n"
                "The article PMC IDs are in the link filenames (e.g., ncbi_11918561_links.txt → PMC11918561)."
            )
            logger.info(alternative_msg)
            print(alternative_msg)
        
        return successful_downloads
