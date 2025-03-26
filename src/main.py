import argparse
import os
from pathlib import Path
import logging
import datetime
import sys

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
        xml_files = source_handler.save_efetch_xml_responses(pmc_ids)
        print(f"✅ Saved {len(xml_files)} XML response files")
    
        # Print the first few file paths to help locate them
        if xml_files:
            print("\nSaved XML files (first 3):")
            for i, file_path in enumerate(xml_files[:3]):
                print(f"  {i+1}. {file_path}")
            if len(xml_files) > 3:
                print(f"  ... and {len(xml_files) - 3} more files")
    
    # Get supplementary materials
    print("\nLooking for supplementary materials...")
    results = source_handler.get_supplementary_files(pmc_ids)
    
    # Display results
    display_service = DisplayService()
    display_service.display_results(results)
    
    # Save results
    if results:
        print("\nSaving links to files...")
        data_collector = DataCollector()
        data_collector.batch_save_links(results, source_type="ncbi")
        print("Links saved successfully")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
