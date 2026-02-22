"""AI-controlled dynamic web scraping service."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIWebScraperService:
    """AI-controlled web scraping that scrapes on-demand based on AI needs."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def get_scraping_tools_prompt(self) -> str:
        """Get prompt that teaches AI how to use scraping tools."""
        return """
AVAILABLE TOOLS:

1. SEARCH_WEB(query: str) - Search Google for information
   Use when: You need current information, facts, news, or data you don't have
   Example: SEARCH_WEB("Virat Kohli latest match 2025")

2. SCRAPE_URL(url: str) - Extract content from a specific webpage
   Use when: You have a URL and need detailed content from it
   Example: SCRAPE_URL("https://www.espncricinfo.com/...")

3. DEEP_SEARCH(query: str, num_sources: int) - Search and scrape multiple sources
   Use when: You need comprehensive information from multiple sources
   Example: DEEP_SEARCH("Python async programming tutorial", 5)

HOW TO USE:
- If you don't have information, use these tools
- Put tool calls in your response like: [TOOL: SEARCH_WEB("query here")]
- You can use multiple tools in one response
- After getting results, synthesize the information naturally

WHEN TO USE:
- User asks about current events, news, or recent information
- User asks about specific facts you're unsure about
- User wants detailed information on a topic
- You need to verify or update your knowledge
"""
    
    def search_web(self, query: str) -> str:
        """Search Google and return formatted results."""
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}&num=5"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for i, result in enumerate(soup.select('div.g')[:5], 1):
                title = result.select_one('h3')
                snippet = result.select_one('div.VwiC3b, span.aCOpRe')
                link = result.select_one('a')
                
                if title and link:
                    url = link.get('href', '')
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    results.append(f"{i}. {title.get_text()}\n   {snippet.get_text() if snippet else ''}\n   URL: {url}")
            
            return "\n\n".join(results) if results else "No results found"
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search failed: {str(e)}"
    
    def scrape_url(self, url: str) -> str:
        """Scrape content from a specific URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # Extract main content
            main = soup.find('article') or soup.find('main') or soup.find('body')
            if not main:
                return "Could not extract content"
            
            # Get text
            paragraphs = [p.get_text(strip=True) for p in main.find_all(['p', 'h1', 'h2', 'h3']) if len(p.get_text(strip=True)) > 30]
            
            content = '\n\n'.join(paragraphs[:20])  # First 20 paragraphs
            return content[:5000] if content else "No content found"
        except Exception as e:
            logger.error(f"Scrape error: {e}")
            return f"Scraping failed: {str(e)}"
    
    def deep_search(self, query: str, num_sources: int = 5) -> str:
        """Search and scrape multiple sources."""
        try:
            # First search
            search_results = self.search_web(query)
            
            # Extract URLs from search results
            urls = []
            for line in search_results.split('\n'):
                if line.strip().startswith('URL:'):
                    url = line.replace('URL:', '').strip()
                    if url.startswith('http'):
                        urls.append(url)
            
            # Scrape top URLs
            scraped_content = []
            for i, url in enumerate(urls[:num_sources], 1):
                content = self.scrape_url(url)
                if content and not content.startswith('Scraping failed'):
                    scraped_content.append(f"=== SOURCE {i}: {url} ===\n{content[:2000]}")
            
            return "\n\n".join(scraped_content) if scraped_content else search_results
        except Exception as e:
            logger.error(f"Deep search error: {e}")
            return f"Deep search failed: {str(e)}"
    
    def process_ai_response(self, response: str) -> tuple[str, bool]:
        """
        Process AI response to detect and execute tool calls.
        Returns (processed_response, tools_were_used)
        """
        import re
        
        # Detect tool calls
        tool_pattern = r'\[TOOL:\s*(\w+)\("([^"]+)"\)\]'
        matches = re.findall(tool_pattern, response)
        
        if not matches:
            return response, False
        
        # Execute tools
        tool_results = []
        for tool_name, arg in matches:
            if tool_name == "SEARCH_WEB":
                result = self.search_web(arg)
                tool_results.append(f"Search results for '{arg}':\n{result}")
            elif tool_name == "SCRAPE_URL":
                result = self.scrape_url(arg)
                tool_results.append(f"Content from {arg}:\n{result}")
            elif tool_name == "DEEP_SEARCH":
                parts = arg.split(',')
                query = parts[0].strip()
                num = int(parts[1].strip()) if len(parts) > 1 else 5
                result = self.deep_search(query, num)
                tool_results.append(f"Deep search for '{query}':\n{result}")
        
        # Remove tool calls from response
        cleaned_response = re.sub(tool_pattern, '', response)
        
        # Add tool results
        final_response = cleaned_response + "\n\n--- TOOL RESULTS ---\n" + "\n\n".join(tool_results)
        
        return final_response, True
