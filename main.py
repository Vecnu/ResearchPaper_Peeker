from src.core.source_handlers.ncbi_handler import NCBIHandler
from src.support.logging_service import Logger

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

def main():
    handler = get_source_handler()
    if not handler:
        return
        
    query = input("🔍 Enter search phrase: ").strip()
    if not query:
        print("⚠️ Search phrase cannot be empty!")
        return
        
    articles = handler.search_articles(query)
    metadata = handler.get_article_metadata(articles)
    results = handler.get_supplementary_materials(articles)
    
    # Display results (can be moved to a separate display service)
    # Current display_results logic here

if __name__ == "__main__":
    main()
