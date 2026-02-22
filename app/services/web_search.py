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
            # Try Google first (best for fresh results), fallback to DuckDuckGo
            results = self._search_google(query, max_results)
            if not results:
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
    
    def _search_google(self, query: str, max_results: int) -> list[dict]:
        """Search Google (best for fresh results)."""
        try:
            # Add time filter for recent results
            time_query = f"{query} after:2024"
            url = f"https://www.google.com/search?q={quote_plus(time_query)}&num={max_results}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('div.g')[:max_results]:
                title_elem = result.select_one('h3')
                link_elem = result.select_one('a')
                snippet_elem = result.select_one('div.VwiC3b, span.aCOpRe')
                
                if title_elem and link_elem:
                    url = link_elem.get('href', '')
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    if url and not url.startswith('http'):
                        continue
                    
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'url': url
                    })
            
            return results
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> list[dict]:
        """Search DuckDuckGo HTML."""
        # Add time-based keywords for fresh results
        time_query = f"{query} 2024 2025 latest recent"
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(time_query)}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:max_results]:
            title = result.select_one('.result__title')
            snippet = result.select_one('.result__snippet')
            link_elem = result.select_one('.result__url')
            
            if title and link_elem:
                # Extract actual URL from DuckDuckGo redirect
                url_text = link_elem.get('href', '')
                if url_text.startswith('//duckduckgo.com/l/?uddg='):
                    # Parse the redirect URL
                    try:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(url_text)
                        actual_url = parse_qs(parsed.query).get('uddg', [''])[0]
                        if actual_url:
                            url_text = actual_url
                    except:
                        pass
                
                if url_text.startswith('//'):
                    url_text = 'https:' + url_text
                
                results.append({
                    'title': title.get_text(strip=True),
                    'snippet': snippet.get_text(strip=True) if snippet else '',
                    'url': url_text
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
            # Skip DuckDuckGo redirect URLs
            if 'duckduckgo.com' in url:
                return None
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 
                           'iframe', 'noscript', 'svg', 'form', 'button', 'ad']):
                tag.decompose()
            
            # Extract main content with priority selectors
            main_content = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=re.compile(r'content|article|post|entry|body', re.I)) or
                soup.find('div', id=re.compile(r'content|article|main', re.I)) or
                soup.find('body')
            )
            
            if not main_content:
                return None
            
            # Extract text with structure - prioritize recent content
            paragraphs = []
            for elem in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li', 'span', 'div']):
                text = elem.get_text(strip=True)
                # Filter and prioritize content with dates/numbers
                if len(text) > 30:
                    paragraphs.append(text)
            
            # Extract tables (useful for match stats)
            tables = []
            for table in main_content.find_all('table')[:2]:
                table_text = table.get_text(separator=' | ', strip=True)
                if len(table_text) > 20:
                    tables.append(table_text[:500])
            
            # Combine content
            full_text = ' '.join(paragraphs)
            if tables:
                full_text += '\n\nTABLE DATA: ' + ' '.join(tables)
            
            return {
                'title': title,
                'text': full_text[:4000],  # Increased limit for more context
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
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        output = f"USER QUESTION: {query}\n\n"
        output += f"TODAY'S DATE: {current_date}\n\n"
        output += "CONTEXT: Below is web data scraped from search results.\n"
        output += "CRITICAL INSTRUCTIONS:\n"
        output += "1. ONLY use information explicitly stated in the context below\n"
        output += "2. DO NOT invent, assume, or hallucinate ANY information\n"
        output += "3. If the context lacks recent/accurate data, say: 'The available sources do not contain current information'\n"
        output += "4. DO NOT make up dates, scores, match details, or events\n"
        output += "5. If information seems outdated or contradictory, acknowledge it\n\n"
        
        # Provide web content
        for i, result in enumerate(results[:5], 1):
            output += f"--- Source: {result['title']} ---\n"
            
            if result['url'] in contents:
                content = contents[result['url']]
                output += f"{content['text'][:3000]}\n\n"
            else:
                output += f"{result['snippet']}\n\n"
        
        output += "\n--- END OF CONTEXT ---\n\n"
        output += f"Answer: {query}\n\n"
        output += "RESPONSE RULES:\n"
        output += "- If context has the answer: Provide it naturally with specific details\n"
        output += "- If context is outdated: Say 'Based on available sources from [date/period], ...' and suggest checking official sites\n"
        output += "- If context lacks info: Say 'I cannot find current information in the available sources. Please check [official sites]'\n"
        output += "- NEVER invent information not in the context\n"
        
        return output
