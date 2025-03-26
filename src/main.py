import argparse
import os
from pathlib import Path
import logging
import datetime
import sys
import requests  # Make sure this is added

# Import your modules using relative imports
from core.source_handlers.ncbi_handler import NCBIHandler
from infrastructure.data_collector import DataCollector
from support.display_service import DisplayService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResearchPaperPeeker")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="ResearchPaper_Peeker - Search and download supplementary materials")
    parser.add_argument("--save-xml", action="store_true", help="Save XML responses for debugging")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results to return")
    parser.add_argument("--download-only", action="store_true", help="Only download files from existing links")
    return parser.parse_args()

def get_source_handler():
    """Get the source handler based on user selection"""
    sources = {
        "1": ("NCBI", NCBIHandler),
        "2": ("Google Scholar", None)  # To be implemented
    }
    
    logger.info("Available sources:")
    for key, (name, _) in sources.items():
        print(f"{key}: {name}")
        
    choice = input("Select source (1-2): ").strip()
    
    if choice in sources:
        name, handler_class = sources[choice]
        if handler_class:
            logger.info(f"Selected source: {name}")
            return handler_class()
        logger.warning(f"{name} handler not implemented yet")
        print(f"{name} handler not implemented yet")
        return None
    
    logger.warning(f"Invalid source selection: {choice}")
    print("Invalid source selection")
    return None

def save_xml_responses(source_handler, article_ids, output_dir=None):
    """
    Fetch XML responses for given PMC IDs using efetch and save them to files.
    
    Args:
        source_handler: The source handler (to get the base_url)
        article_ids: List of PMC IDs
        output_dir: Directory to save XML files (optional)
        
    Returns:
        List of paths to saved XML files
    """
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
            efetch_url = f"{source_handler.base_url}/efetch.fcgi"
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

def main():
    """Main function to run the application"""
    # Parse command line arguments
    args = parse_arguments()
    
    print("ResearchPaper_Peeker - Find and Download Supplementary Materials")
    print("---------------------------------------------------------------")
    
    # Get the source handler
    source_handler = get_source_handler()
    if not source_handler:
        return
    
    # Get user query
    query = input("\nEnter your search query: ").strip()
    if not query:
        print("Search query cannot be empty")
        return
    
    # Set maximum results
    max_results = args.max_results
    
    # Search for articles
    print(f"\nSearching for articles with keyword: '{query}'...")
    pmc_ids = source_handler.search_articles(query, max_results)
    
    if not pmc_ids:
        print("No articles found")
        return
    
    print(f"Found {len(pmc_ids)} articles")
    
    # For debugging: Save the XML responses if flag is set
    if args.debug or args.save_xml:
        print("\n📄 Saving XML responses for debugging...")
        try:
            xml_files = save_xml_responses(source_handler, pmc_ids)
            print(f"✅ Saved {len(xml_files)} XML response files")
            
            # Print the first few file paths to help locate them
            if xml_files:
                print("\nSaved XML files (first 3):")
                for i, file_path in enumerate(xml_files[:3]):
                    print(f"  {i+1}. {file_path}")
                if len(xml_files) > 3:
                    print(f"  ... and {len(xml_files) - 3} more files")
        except Exception as e:
            print(f"❌ Error saving XML responses: {e}")
    
    # Get supplementary materials
    print("\nLooking for supplementary materials...")
    results = source_handler.get_supplementary_materials(pmc_ids)
    
    # Display results
    display_service = DisplayService()
    display_service.display_results(results)
    
    # Save results
    data_collector = DataCollector()
    if results:
        print("\nSaving links to files...")
        data_collector.batch_save_links(results, source_type="ncbi")
        print("Links saved successfully")
        
        # If download-only mode is selected, just download files from existing links
        if args.download_only:
            print("Download-only mode: Processing existing link files...")
            data_collector = DataCollector()
            output_dir = data_collector.create_date_folder()
            data_collector.download_all_documents(output_dir)
            return
        
        # Ask user if they want to download the files now
        download_now = input("\nWould you like to download all supplementary materials now? (y/n): ").strip().lower()
        if download_now == 'y' or download_now == 'yes':
            print("\nDownloading supplementary materials...")
            data_collector.download_all_documents()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
