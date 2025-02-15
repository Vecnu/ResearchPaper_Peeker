class DisplayService:
    def display_results(self, article_info):
        total_articles = len(article_info)
        found_supplements = False
        articles_with_supplements = 0
        
        print(f"🔍 Total articles found: {total_articles}")
        
        for pmc_id, info in article_info.items():
            if info["links"]:
                found_supplements = True
                articles_with_supplements += 1
                print(f"📝 **{info['title']}** (PMC{pmc_id})")
                for link in info["links"]:
                    print(f"   📎 {link}")
                print("\n" + "-" * 60)

        print(f"📊 Articles with supplementary materials: {articles_with_supplements}")
        
        if not found_supplements:
            print("❌ No supplementary materials found for the retrieved articles.")