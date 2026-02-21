"""Advanced web search with recursive content extraction."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import re

logger = logging.getLogger(__name__)

class WebSearchService:
    """Advanced web search with deep content extraction."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 8
        self.max_depth = 2
    
    def search(self, query: str, max_results: int = 8) -> tuple[str, list[str]]:
        """Search and extract content. Returns (formatted_text, source_urls)."""
        try:
            results = self._search_duckduckgo(query, max_results)
            
            if not results:
                return "No search results found.", []
            
            # Extract content from top 5 results in parallel
            contents = self._extract_contents_parallel(results[:5])
            
            # Get source URLs
            source_urls = [r['url'] for r in results[:5]]
            
            # Format for AI with citations
            formatted = self._format_for_ai(query, results, contents)
            
            return formatted, source_urls
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search failed: {str(e)}", []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> list[dict]:
        """Search DuckDuckGo."""
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:max_results]:
            title = result.select_one('.result__title')
            snippet = result.select_one('.result__snippet')
            link = result.select_one('.result__url')
            
            if title and link:
                url = link.get('href', '')
                if url.startswith('//'):
                    url = 'https:' + url
                
                results.append({
                    'title': title.get_text(strip=True),
                    'snippet': snippet.get_text(strip=True) if snippet else '',
                    'url': url
                })
        
        return results
    
    def _extract_contents_parallel(self, results: list[dict]) -> dict[str, dict]:
        """Extract content from URLs in parallel."""
        contents = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_result = {
                executor.submit(self._extract_content_recursive, r['url'], r['title']): r 
                for r in results
            }
            
            for future in as_completed(future_to_result):
                result = future_to_result[future]
                try:
                    content_data = future.result()
                    if content_data:
                        contents[result['url']] = content_data
                except Exception as e:
                    logger.error(f"Extraction failed for {result['url']}: {e}")
        
        return contents
    
    def _extract_content_recursive(self, url: str, title: str, depth: int = 0) -> Optional[dict]:
        """Recursively extract content from URL and linked pages."""
        if depth >= self.max_depth:
            return None
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 
                           'iframe', 'noscript', 'svg', 'form', 'button']):
                tag.decompose()
            
            # Extract main content
            main_content = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=re.compile(r'content|article|post|entry', re.I)) or
                soup.find('body')
            )
            
            if not main_content:
                return None
            
            # Extract text with structure
            paragraphs = []
            for p in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = p.get_text(strip=True)
                if len(text) > 30:  # Filter short fragments
                    paragraphs.append(text)
            
            # Extract code blocks
            code_blocks = []
            for code in main_content.find_all(['code', 'pre']):
                code_text = code.get_text(strip=True)
                if len(code_text) > 10:
                    code_blocks.append(code_text)
            
            # Combine content
            full_text = ' '.join(paragraphs)
            
            # Extract key links for recursive search (depth 1 only)
            related_content = []
            if depth == 0:
                for link in main_content.find_all('a', href=True)[:3]:
                    link_url = urljoin(url, link['href'])
                    if self._is_valid_url(link_url, url):
                        sub_content = self._extract_content_recursive(link_url, link.get_text(strip=True), depth + 1)
                        if sub_content:
                            related_content.append(sub_content['text'][:500])
            
            return {
                'title': title,
                'text': full_text[:3000],
                'code': code_blocks[:2] if code_blocks else [],
                'related': related_content,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Extract error for {url}: {e}")
            return None
    
    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid for recursive extraction."""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            
            # Same domain only
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Skip non-content URLs
            skip_patterns = ['login', 'signup', 'cart', 'checkout', 'download', 'pdf']
            if any(pattern in url.lower() for pattern in skip_patterns):
                return False
            
            return True
        except:
            return False
    
    def _format_for_ai(self, query: str, results: list[dict], contents: dict[str, dict]) -> str:
        """Format search results as supplementary information for AI."""
        output = f"USER QUESTION: {query}\n\n"
        output += "IMPORTANT: Below is CURRENT web data to answer the question above.\n"
        output += "Read this information carefully and use it in your answer.\n\n"
        
        # Provide web content
        for i, result in enumerate(results[:5], 1):
            output += f"=== WEB SOURCE {i}: {result['title']} ===\n"
            
            if result['url'] in contents:
                content = contents[result['url']]
                output += f"{content['text'][:2000]}\n\n"
                
                if content.get('code'):
                    output += f"CODE:\n{content['code'][0][:400]}\n\n"
            else:
                output += f"{result['snippet']}\n\n"
        
        output += "\n=== END OF WEB DATA ===\n\n"
        output += f"Now answer the question: {query}\n"
        output += "Use the web information above. Include specific details from the sources.\n"
        
        return output
