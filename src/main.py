from src.core.source_handlers.ncbi_handler import NCBIHandler
from src.support.logging_service import Logger
from src.infrastructure.data_collector import DataCollector

# Get logger instance
logger = Logger.get_instance()

def get_source_handler():
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
    logger.info("Starting ResearchPaper_Peeker application")
    
    # Create a data collector instance
    collector = DataCollector()
    
    try:
        handler = get_source_handler()
        if not handler:
            logger.warning("No valid source handler selected. Exiting.")
            return
            
        query = input("🔍 Enter search phrase: ").strip()
        if not query:
            logger.warning("Search phrase cannot be empty. Exiting.")
            print("⚠️ Search phrase cannot be empty!")
            return
            
        logger.info(f"Searching for articles with query: '{query}'")
        articles = handler.search_articles(query)
        logger.info(f"Found {len(articles)} articles")
        
        metadata = handler.get_article_metadata(articles)
        logger.info(f"Retrieved metadata for {len(metadata)} articles")
        
        logger.info("Retrieving supplementary materials...")
        results = handler.get_supplementary_materials(articles)
        logger.info(f"Retrieved supplementary materials from {len(results)} articles")
        
        # Log the structure of results to help debug
        logger.debug(f"Results type: {type(results)}")
        if results:
            if isinstance(results, dict):
                sample_key = next(iter(results))
                logger.debug(f"Sample key: {sample_key}, Value type: {type(results[sample_key])}")
            elif isinstance(results, list) and results:
                logger.debug(f"First item type: {type(results[0])}")
        
        try:
            # Save links to files
            logger.info("Saving supplementary links to files...")
            collector.batch_save_links(results, source_type="ncbi")
            
            # Try to handle different result formats for display
            logger.info("Displaying results...")
            if isinstance(results, dict):
                display_results(results)
            elif isinstance(results, list):
                # Convert list to expected format if needed
                formatted_results = {}
                for item in results:
                    if isinstance(item, dict) and 'pmc_id' in item and 'links' in item:
                        formatted_results[item['pmc_id']] = item['links']
                display_results(formatted_results)
            else:
                logger.error(f"Unexpected results format: {type(results)}")
                
        except Exception as e:
            logger.error(f"Error processing results: {str(e)}")
            
        # Print summary
        collector.print_summary()
        
    except Exception as e:
        logger.exception(f"Unexpected error in main application: {str(e)}")
        print(f"❌ An error occurred. Check logs/errors.log for details.")
    
    logger.info("Application completed")

def display_results(results):
    """
    Display the results of the supplementary materials search
    
    Args:
        results: Dictionary with PMC IDs as keys and lists of links as values
    """
    if not results:
        logger.info("No results to display.")
        print("No results to display.")
        return
    
    print("\n🔍 Search Results Summary:")
    print(f"📚 Articles with supplementary materials: {len(results)}")
    
    total_links = sum(len(links) for links in results.values() if links)
    print(f"📎 Total supplementary materials found: {total_links}")
    
    # Display some samples if there are many results
    if len(results) > 5:
        print("\n📋 Sample of articles with supplementary materials:")
        for pmc_id, links in list(results.items())[:5]:
            if links:
                print(f"  • PMC{pmc_id}: {len(links)} supplementary files")
        print(f"  • ... and {len(results) - 5} more articles")
    else:
        print("\n📋 Articles with supplementary materials:")
        for pmc_id, links in results.items():
            if links:
                print(f"  • PMC{pmc_id}: {len(links)} supplementary files")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger = Logger.get_instance()
        logger.exception(f"Unhandled exception in main: {str(e)}")
        print(f"❌ An unexpected error occurred. Check logs/errors.log for details.")
