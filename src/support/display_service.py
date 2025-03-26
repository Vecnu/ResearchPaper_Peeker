class DisplayService:
    def display_results(self, results):
        """
        Display the results of the supplementary materials search
        
        Args:
            results: Dictionary with PMC IDs as keys and lists of links as values
        """
        if not results:
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