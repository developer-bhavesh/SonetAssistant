"""Advanced web search with robust scraping."""
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
    
    def __init__(self, proxies: Optional[list[str]] = None):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        self.timeout = 10
        self.proxies = proxies or []
        self.proxy_index = 0
        self.ua_index = 0
        self.session = requests.Session()
    
    def _get_headers(self) -> dict:
        """Get headers with rotating user agent."""
        self.ua_index = (self.ua_index + 1) % len(self.user_agents)
        return {
            'User-Agent': self.user_agents[self.ua_index],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _get_proxy(self) -> Optional[dict]:
        """Get next proxy in rotation."""
        if not self.proxies:
            return None
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        proxy = self.proxies[self.proxy_index]
        return {'http': proxy, 'https': proxy}
    
    def search(self, query: str, max_results: int = 8) -> tuple[str, list[str]]:
        """Search using multiple engines with fallback chain."""
        try:
            # Try Google, DuckDuckGo, then Startpage
            search_engines = [
                ('Google', self._search_google),
                ('DuckDuckGo', self._search_duckduckgo),
                ('Startpage', self._search_startpage)
            ]
            
            results = []
            for engine_name, search_func in search_engines:
                try:
                    results = search_func(query, max_results)
                    if results:
                        logger.info(f"Got {len(results)} results from {engine_name}")
                        break
                except Exception as e:
                    logger.warning(f"{engine_name} failed: {e}")
                    continue
            
            # Return "no results" message if all engines failed
            if not results:
                no_results_msg = self._format_for_ai(query, [], {})
                return no_results_msg, []
            
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
    

    
    def _search_startpage(self, query: str, max_results: int) -> list[dict]:
        """Search Startpage with proxy support."""
        try:
            url = f"https://www.startpage.com/sp/search?query={quote_plus(query)}&language=english"
            headers = self._get_headers()
            proxy = self._get_proxy()
            
            response = requests.get(url, headers=headers, proxies=proxy, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('div.w-gl__result')[:max_results]:
                title_elem = result.select_one('a.w-gl__result-title')
                snippet_elem = result.select_one('p.w-gl__description')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'url': title_elem.get('href', '')
                    })
            return results
        except Exception as e:
            logger.error(f"Startpage search error: {e}")
            return []
    
    def _search_google(self, query: str, max_results: int) -> list[dict]:
        """Search Google with proxy support."""
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}&hl=en"
            headers = self._get_headers()
            proxy = self._get_proxy()
            
            response = requests.get(url, headers=headers, proxies=proxy, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('div.g')[:max_results]:
                title_elem = result.select_one('h3')
                link_elem = result.select_one('a')
                snippet_elem = result.select_one('div.VwiC3b, span.aCOpRe, div.IsZvec')
                
                if title_elem and link_elem:
                    url_text = link_elem.get('href', '')
                    if url_text.startswith('/url?q='):
                        url_text = url_text.split('/url?q=')[1].split('&')[0]
                    
                    if url_text and url_text.startswith('http'):
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                            'url': url_text
                        })
            
            return results
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    

    
    def _search_duckduckgo(self, query: str, max_results: int) -> list[dict]:
        """Search DuckDuckGo with proxy support."""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = self._get_headers()
            proxy = self._get_proxy()
            
            response = requests.get(url, headers=headers, proxies=proxy, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result')[:max_results]:
                title = result.select_one('.result__title')
                snippet = result.select_one('.result__snippet')
                link_elem = result.select_one('.result__url')
                
                if title and link_elem:
                    url_text = link_elem.get('href', '')
                    if url_text.startswith('//duckduckgo.com/l/?uddg='):
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
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _extract_contents_parallel(self, results: list[dict]) -> dict[str, dict]:
        """Extract content from URLs in parallel."""
        contents = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_result = {
                executor.submit(self._extract_content, r['url'], r['title']): r 
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
    
    def _extract_content(self, url: str, title: str) -> Optional[dict]:
        """Extract content from URL with proxy support."""
        try:
            # Skip invalid URLs
            if 'duckduckgo.com' in url or not url.startswith('http'):
                return None
            
            headers = self._get_headers()
            proxy = self._get_proxy()
            
            response = requests.get(url, headers=headers, proxies=proxy, timeout=self.timeout, allow_redirects=True)
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
            
            # Extract text with structure
            paragraphs = []
            for elem in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li', 'span', 'div']):
                text = elem.get_text(strip=True)
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
                'text': full_text[:4000],
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Extract error for {url}: {e}")
            return None
    

    
    def _format_for_ai(self, query: str, results: list[dict], contents: dict[str, dict]) -> str:
        """Format search results for AI with clear instructions."""
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        if not results:
            return f"=== WEB SEARCH RESULTS (Retrieved: {current_date}) ===\n\nQuery: {query}\n\nNo results found. The search returned no information.\n\n=== END WEB SEARCH RESULTS ===\n\nYou MUST tell the user that no current information was found in the search."
        
        output = f"=== WEB SEARCH RESULTS (Retrieved: {current_date}) ===\n\n"
        output += f"Query: {query}\n\n"
        output += "CRITICAL: Use ONLY the information below. Do NOT use your training data. If the information below doesn't answer the query, say so.\n\n"
        
        # Provide web content
        for i, result in enumerate(results[:5], 1):
            output += f"[Source {i}] {result['title']}\n"
            
            if result['url'] in contents:
                content = contents[result['url']]
                output += f"{content['text'][:3000]}\n\n"
            else:
                output += f"{result['snippet']}\n\n"
        
        output += "=== END WEB SEARCH RESULTS ===\n\n"
        output += "Answer using ONLY the information above. If it doesn't contain the answer, say: 'The search results don't contain information about this.'\n"
        
        return output
