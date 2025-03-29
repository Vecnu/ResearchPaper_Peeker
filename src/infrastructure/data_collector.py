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

    def extract_zip_files(self, documents_dir=None):
        """
        Extract all .zip files in the documents directory directly into the documents directory
        
        Args:
            documents_dir: Directory containing the downloaded files (optional)
        
        Returns:
            Number of successfully extracted zip files
        """
        import zipfile
        import os
        from pathlib import Path
        import logging
        from support.logging_service import Logger
        
        # Get logger instance
        logger = Logger.get_instance()
        
        # Use default documents directory if none is specified
        if documents_dir is None:
            if self.current_output_dir is None:
                logger.warning("No output directory specified and no current directory set.")
                print("No output directory specified and no current directory set.")
                return 0
            documents_dir = self.current_output_dir / "documents"
        else:
            documents_dir = Path(documents_dir)
        
        if not documents_dir.exists():
            logger.warning(f"Documents directory not found: {documents_dir}")
            print(f"Documents directory not found: {documents_dir}")
            return 0
        
        # Find all .zip files in the documents directory
        zip_files = list(documents_dir.glob("*.zip"))
        if not zip_files:
            logger.info("No zip files found to extract.")
            print("No zip files found to extract.")
            return 0
        
        logger.info(f"Found {len(zip_files)} zip files to extract.")
        print(f"Found {len(zip_files)} zip files to extract.")
        
        # Statistics
        successful_extractions = 0
        failed_extractions = 0
        total_files_extracted = 0
        
        # Process each zip file
        for zip_file_path in zip_files:
            try:
                logger.info(f"Extracting {zip_file_path.name} directly to documents directory...")
                print(f"Extracting {zip_file_path.name} directly to documents directory...")
                
                # Extract the zip file
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    # Check for potentially harmful paths (zip slip vulnerability protection)
                    files_to_extract = []
                    for zip_info in zip_ref.infolist():
                        if zip_info.filename.startswith('..') or zip_info.filename.startswith('/'):
                            logger.warning(f"Skipping potentially unsafe path in zip file: {zip_info.filename}")
                            continue
                        
                        # Skip directories
                        if zip_info.filename.endswith('/'):
                            continue
                        
                        # Get just the filename (ignore path)
                        filename = os.path.basename(zip_info.filename)
                        
                        # If empty filename, skip
                        if not filename:
                            continue
                        
                        # Check if target file already exists
                        target_path = documents_dir / filename
                        if target_path.exists():
                            # Create a unique name to avoid conflicts
                            base_name = target_path.stem
                            extension = target_path.suffix
                            counter = 1
                            while target_path.exists():
                                new_name = f"{base_name}_{counter}{extension}"
                                target_path = documents_dir / new_name
                                counter += 1
                            
                            # Rename the file in the extraction process
                            zip_info.filename = new_name
                        else:
                            zip_info.filename = filename
                        
                        files_to_extract.append(zip_info)
                    
                    # Extract files one by one with controlled filenames
                    for zip_info in files_to_extract:
                        zip_ref.extract(zip_info, documents_dir)
                        total_files_extracted += 1
                
                successful_extractions += 1
                logger.info(f"Successfully extracted {len(files_to_extract)} files from {zip_file_path.name}")
                print(f"✅ Successfully extracted {len(files_to_extract)} files from {zip_file_path.name}")
                
            except zipfile.BadZipFile as e:
                error_msg = f"Error extracting {zip_file_path.name}: Not a valid zip file"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                failed_extractions += 1
            except Exception as e:
                error_msg = f"Error extracting {zip_file_path.name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                print(f"❌ {error_msg}")
                failed_extractions += 1
        
        # Print summary
        summary = f"\n📊 Extraction Summary:\n" \
                  f"  Total zip files: {len(zip_files)}\n" \
                  f"  Total files extracted: {total_files_extracted}\n" \
                  f"  Successfully processed zip files: {successful_extractions}\n" \
                  f"  Failed zip files: {failed_extractions}"
        
        logger.info(summary)
        print(summary)
        
        return successful_extractions

    def clean_documents_directory(self, documents_dir=None):
        """
        Clean the documents directory by removing files that aren't research documents
        (excluding spreadsheets)
        
        Args:
            documents_dir: Directory containing the documents (optional)
        
        Returns:
            Number of files removed
        """
        import os
        from pathlib import Path
        import logging
        from support.logging_service import Logger
        
        # Get logger instance
        logger = Logger.get_instance()
        
        # Use default documents directory if none is specified
        if documents_dir is None:
            if self.current_output_dir is None:
                logger.warning("No output directory specified and no current directory set.")
                print("No output directory specified and no current directory set.")
                return 0
            documents_dir = self.current_output_dir / "documents"
        else:
            documents_dir = Path(documents_dir)
        
        if not documents_dir.exists():
            logger.warning(f"Documents directory not found: {documents_dir}")
            print(f"Documents directory not found: {documents_dir}")
            return 0
        
        # Define allowed document extensions (case insensitive)
        # Note: Spreadsheets (.xls, .xlsx, .csv, .tsv, .ods) have been removed
        allowed_extensions = {
            # Text documents
            ".txt", ".doc", ".docx", ".rtf", ".odt", ".md", ".tex",
            # PDFs
            ".pdf",
            # Data formats
            ".json", ".xml", ".yaml", ".yml",
            # Research specific formats
            ".nb", ".ipynb", ".r", ".rmd", ".mat", ".sav", ".sas7bdat", ".dta",
            # Code (potentially part of research)
            ".py", ".r", ".m", ".do"
        }
        
        # Explicitly define spreadsheet extensions to highlight they're being removed
        spreadsheet_extensions = {".xls", ".xlsx", ".csv", ".tsv", ".ods"}
        
        # Find all files in the documents directory
        all_files = list(documents_dir.glob("*"))
        
        # Count files by type
        file_type_counts = {}
        removed_files = []
        kept_files = []
        
        for file_path in all_files:
            if file_path.is_dir():
                continue  # Skip directories
            
            extension = file_path.suffix.lower()
            
            # Count file types
            if extension not in file_type_counts:
                file_type_counts[extension] = 0
            file_type_counts[extension] += 1
            
            # Check if we should keep this file
            if extension in allowed_extensions:
                kept_files.append(file_path)
            else:
                removed_files.append(file_path)
                # Highlight spreadsheets being removed
                if extension in spreadsheet_extensions:
                    logger.info(f"Spreadsheet found for removal: {file_path.name}")
        
        # Log file type statistics
        logger.info(f"File types found in documents directory:")
        for ext, count in file_type_counts.items():
            if ext in spreadsheet_extensions:
                keep_status = "Remove (Spreadsheet)"
            else:
                keep_status = "Keep" if ext in allowed_extensions else "Remove"
            logger.info(f"  {ext}: {count} files ({keep_status})")
        
        # Ask user to confirm removal
        if removed_files:
            spreadsheet_count = sum(1 for f in removed_files if f.suffix.lower() in spreadsheet_extensions)
            other_count = len(removed_files) - spreadsheet_count
            
            print(f"\nFound {len(removed_files)} files to remove:")
            if spreadsheet_count > 0:
                print(f"  - {spreadsheet_count} spreadsheet files")
            if other_count > 0:
                print(f"  - {other_count} other non-document files")
            
            for ext, count in file_type_counts.items():
                if ext not in allowed_extensions:
                    status = "(Spreadsheet)" if ext in spreadsheet_extensions else ""
                    print(f"  {ext}: {count} files {status}")
            
            confirm = input("\nDo you want to remove these non-document files? (y/n): ").strip().lower()
            
            if confirm == 'y' or confirm == 'yes':
                # Remove files
                for file_path in removed_files:
                    try:
                        os.remove(file_path)
                        if file_path.suffix.lower() in spreadsheet_extensions:
                            logger.info(f"Removed spreadsheet: {file_path.name}")
                        else:
                            logger.info(f"Removed: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Error removing {file_path.name}: {str(e)}")
            
                print(f"✅ Removed {len(removed_files)} files in total:")
                if spreadsheet_count > 0:
                    print(f"   - {spreadsheet_count} spreadsheet files")
                if other_count > 0:
                    print(f"   - {other_count} other non-document files")
            else:
                print("File removal cancelled.")
                return 0
        else:
            print("No non-document files found to remove.")
            return 0
        
        # Print summary
        summary = f"\n📊 Cleanup Summary:\n" \
                  f"  Total files scanned: {len(all_files)}\n" \
                  f"  Files kept: {len(kept_files)}\n" \
                  f"  Files removed: {len(removed_files)} ({spreadsheet_count} spreadsheets)"
        
        logger.info(summary)
        print(summary)
        
        return len(removed_files)
