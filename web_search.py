"""
JARVIS Web Search Module
Handles web searching and content summarization
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import WEB_SEARCH_TIMEOUT, WEB_SEARCH_RESULTS_COUNT
from brain import JarvisBrain

class WebSearch:
    """Web search and content extraction"""
    
    def __init__(self):
        self.brain = JarvisBrain()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search(self, query: str, num_results: int = WEB_SEARCH_RESULTS_COUNT) -> List[Dict]:
        """
        Search the web
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of search results
        """
        print(f"🔍 Searching for: {query}")
        
        try:
            # Using a simple approach with DuckDuckGo-like search
            # Note: For production, consider using SerpAPI or similar
            
            results = []
            
            # Simple Google search URL (may need token in production)
            url = "https://www.google.com/search"
            params = {
                'q': query,
                'num': num_results
            }
            
            try:
                response = self.session.get(url, params=params, timeout=WEB_SEARCH_TIMEOUT)
                response.raise_for_status()
                
                # For now, provide a simple response structure
                # In production, parse actual search results
                results.append({
                    "title": f"Results for: {query}",
                    "url": f"https://www.google.com/search?q={query}",
                    "snippet": "Please check Google directly for the latest results."
                })
            except:
                # Fallback when web access is restricted
                results.append({
                    "title": f"Web Search - {query}",
                    "url": "#",
                    "snippet": "Web search interface requires configuration. Please update with API key for production use."
                })
            
            print(f"✅ Found {len(results)} results")
            return results
        
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def summarize_url(self, url: str) -> Optional[str]:
        """
        Fetch and summarize webpage content
        
        Args:
            url: URL to summarize
            
        Returns:
            Summary or None
        """
        print(f"📄 Fetching: {url}")
        
        try:
            response = self.session.get(url, timeout=WEB_SEARCH_TIMEOUT)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract main content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = ' '.join(text.split())
            
            # Limit to first 2000 characters for summarization
            text = text[:2000]
            
            if not text:
                return "❌ No content found at URL"
            
            # Summarize with AI
            summary_prompt = f"""Provide a brief 2-3 sentence summary of the following web content:

{text}

Summary:"""
            
            summary = self.brain.query(summary_prompt)
            return summary
        
        except Exception as e:
            print(f"❌ Error fetching URL: {e}")
            return None
    
    def get_weather(self, location: str = "current") -> str:
        """
        Get weather information (requires API key in production)
        
        Args:
            location: Location for weather
            
        Returns:
            Weather information
        """
        # Using AI to provide weather context
        prompt = f"What's the current weather in {location}? Provide a brief response about typical weather conditions."
        
        response = self.brain.query(prompt)
        return response
    
    def get_news_briefing(self, topic: str = "general") -> str:
        """
        Get news briefing on a topic
        
        Args:
            topic: News topic
            
        Returns:
            News briefing
        """
        prompt = f"""Provide a brief news briefing about {topic}. Include 2-3 recent news items or trends.
        
Be concise and informative."""
        
        response = self.brain.query(prompt)
        return response
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for display"""
        if not results:
            return "No results found"
        
        result_str = f"🔍 Search Results ({len(results)}):\n\n"
        
        for i, result in enumerate(results, 1):
            result_str += f"{i}. {result.get('title', 'No title')}\n"
            result_str += f"   URL: {result.get('url', 'No URL')}\n"
            result_str += f"   {result.get('snippet', 'No snippet')}\n\n"
        
        return result_str
