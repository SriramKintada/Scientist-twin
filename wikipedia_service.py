"""Wikipedia integration for fetching scientist biographies"""

import requests
import time
from typing import Optional, Dict

class WikipediaService:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScientistTwin/1.0 (Educational Project)'
        })

    def get_article(self, title: str) -> Optional[Dict]:
        """Fetch Wikipedia article content"""
        try:
            # Get page content
            params = {
                'action': 'query',
                'format': 'json',
                'titles': title,
                'prop': 'extracts|info',
                'exintro': False,
                'explaintext': True,
                'inprop': 'url'
            }

            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            page = next(iter(pages.values()))

            if 'missing' in page:
                return None

            return {
                'title': page.get('title'),
                'extract': page.get('extract', ''),
                'url': page.get('fullurl', ''),
                'pageid': page.get('pageid')
            }

        except Exception as e:
            print(f"Error fetching Wikipedia article for {title}: {e}")
            return None

    def get_article_summary(self, title: str) -> Optional[str]:
        """Get just the summary/extract of an article"""
        article = self.get_article(title)
        if article:
            return article['extract']
        return None

    def search_scientists(self, query: str, domain_keywords: list, limit: int = 10) -> list:
        """Search for scientists on Wikipedia"""
        try:
            search_query = f"{query} Indian scientist {' '.join(domain_keywords)}"

            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': search_query,
                'srlimit': limit
            }

            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('query', {}).get('search', []):
                results.append({
                    'title': item['title'],
                    'snippet': item['snippet'],
                    'pageid': item['pageid']
                })

            return results

        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return []

    def get_multiple_articles(self, titles: list) -> Dict[str, Dict]:
        """Fetch multiple articles efficiently"""
        articles = {}
        for title in titles:
            article = self.get_article(title)
            if article:
                articles[title] = article
            time.sleep(0.5)  # Rate limiting

        return articles
