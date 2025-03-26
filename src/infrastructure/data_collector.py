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
        
        # Use current output directory if none is specified
        if output_dir is None:
            if self.current_output_dir is None:
                print("No output directory specified and no current directory set.")
                return 0
            output_dir = self.current_output_dir
        else:
            output_dir = Path(output_dir)
        
        # Create documents folder if it doesn't exist
        documents_dir = output_dir / "documents"
        os.makedirs(documents_dir, exist_ok=True)
        print(f"Documents will be saved to: {documents_dir}")
        
        # Find all link files in the output directory
        link_files = list(output_dir.glob("*_links.txt"))
        if not link_files:
            print(f"No link files found in {output_dir}")
            return 0
        
        print(f"Found {len(link_files)} link files with supplementary materials.")
        
        # Statistics
        total_links = 0
        successful_downloads = 0
        failed_downloads = 0
        
        # Process each link file
        for link_file in link_files:
            print(f"\nProcessing links from: {link_file.name}")
            
            with open(link_file, 'r') as f:
                links = [line.strip() for line in f if line.strip()]
            
            total_links += len(links)
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
                        print(f"File already exists, skipping: {filename}")
                        successful_downloads += 1
                        continue
                    
                    print(f"Downloading {i+1}/{len(links)}: {filename}...")
                    
                    # Download the file
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Save the file
                    with open(output_path, 'wb') as out_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            out_file.write(chunk)
                    
                    successful_downloads += 1
                    print(f"✅ Successfully downloaded: {filename}")
                    
                    # Brief pause to avoid overwhelming the server
                    time.sleep(0.5)
                    
                except requests.exceptions.RequestException as e:
                    print(f"❌ Failed to download {url}: {str(e)}")
                    failed_downloads += 1
                except Exception as e:
                    print(f"❌ Error processing {url}: {str(e)}")
                    failed_downloads += 1
        
        # Print summary
        print(f"\n📊 Download Summary:")
        print(f"  Total links processed: {total_links}")
        print(f"  Successfully downloaded: {successful_downloads}")
        print(f"  Failed downloads: {failed_downloads}")
        
        return successful_downloads
