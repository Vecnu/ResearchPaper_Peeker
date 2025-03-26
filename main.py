from src.core.source_handlers.ncbi_handler import NCBIHandler
from src.support.logging_service import Logger
from src.infrastructure.data_collector import DataCollector  # Add this import

def get_source_handler():
    sources = {
        "1": ("NCBI", NCBIHandler),
        "2": ("Google Scholar", None)  # To be implemented
    }
    
    print("Available sources:")
    for key, (name, _) in sources.items():
        print(f"{key}: {name}")
        
    choice = input("Select source (1-2): ").strip()
    
    if choice in sources:
        name, handler_class = sources[choice]
        if handler_class:
            return handler_class()
        print(f"{name} handler not implemented yet")
        return None
    
    print("Invalid source selection")
    return None

def main(collector):  # Add collector as a parameter
    handler = get_source_handler()
    if not handler:
        return
        
    query = input("🔍 Enter search phrase: ").strip()
    if not query:
        print("⚠️ Search phrase cannot be empty!")
        return
        
    articles = handler.search_articles(query)
    metadata = handler.get_article_metadata(articles)
    
    # Assuming get_supplementary_materials returns XML content and links for each article
    xml_contents, links_lists = handler.get_supplementary_materials(articles)
    
    # Use the collector to save the links
    if links_lists:
        collector.batch_save_links(articles, links_lists, source_type="ncbi")
    
    # Display results (can be moved to a separate display service)
    # Current display_results logic here

if __name__ == "__main__":
    collector = DataCollector()
    main(collector)  # Pass the collector to main
    collector.print_summary()
