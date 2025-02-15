from core.source_handlers.ncbi_handler import NCBIHandler
from support.display_service import DisplayService

def get_source_handler():
    sources = {
        "1": ("NCBI", NCBIHandler),
        "2": ("Google Scholar", None)
    }
    
    print("Available sources:")
    for key, (name, _) in sources.items():
        print(f"{key}: {name}")
    
    choice = input("Select source (1-2): ").strip()
    return sources.get(choice, (None, None))[1]()

def main():
    handler = get_source_handler()
    if not handler:
        print("Invalid source selection")
        return

    search_query = input("🔍 Enter search phrase (e.g., 'brain MRI'): ").strip()
    if not search_query:
        print("⚠️ Search phrase cannot be empty!")
        return

    article_ids = handler.search_articles(search_query)
    results = handler.get_supplementary_materials(article_ids)
    
    display_service = DisplayService()
    display_service.display_results(results)

if __name__ == "__main__":
    main()
