from abc import ABC, abstractmethod

class BaseSourceHandler(ABC):
    @abstractmethod
    def search_articles(self, query: str, max_results: int = 10):
        pass
    
    @abstractmethod
    def get_article_metadata(self, article_ids: list):
        pass
    
    @abstractmethod
    def get_supplementary_materials(self, article_ids: list):
        pass
