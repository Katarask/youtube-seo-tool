"""YouTube Autocomplete Scraper for keyword suggestions."""

import re
import json
import requests
from typing import Optional
from urllib.parse import quote

from ..data.models import KeywordSuggestion
from ..data.cache import cache
from ..utils.rate_limiter import rate_limiters
from ..utils.logger import logger
from ..constants import MAX_RELATED_SEARCHES_PER_BATCH


class AutocompleteScraper:
    """
    Scrape YouTube's autocomplete API for keyword suggestions.
    
    This uses YouTube's public autocomplete endpoint which doesn't require
    an API key and has no strict rate limits.
    """
    
    BASE_URL = "https://suggestqueries-clients6.youtube.com/complete/search"
    
    def __init__(self, language: str = "en", region: str = "us"):
        self.language = language
        self.region = region
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def _fetch_suggestions(self, query: str) -> list[str]:
        """Fetch raw suggestions from YouTube autocomplete."""
        params = {
            "client": "youtube",
            "ds": "yt",
            "q": query,
            "hl": self.language,
            "gl": self.region,
        }
        
        try:
            rate_limiters.wait("autocomplete")  # Basic rate limiting
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            # Response is JSONP, need to extract JSON
            text = response.text
            
            # Extract JSON from JSONP: window.google.ac.h(JSON)
            match = re.search(r'\[.*\]', text)
            if not match:
                return []
            
            data = json.loads(match.group())
            
            # Structure: [query, [[suggestion1], [suggestion2], ...], ...]
            if len(data) > 1 and isinstance(data[1], list):
                return [item[0] for item in data[1] if item]
            
            return []

        except Exception as e:
            logger.error(f"Error fetching autocomplete for '{query}': {e}")
            return []
    
    def get_suggestions(
        self,
        keyword: str,
        use_cache: bool = True
    ) -> list[KeywordSuggestion]:
        """
        Get autocomplete suggestions for a keyword.
        
        Args:
            keyword: The seed keyword
            use_cache: Whether to use cached results
            
        Returns:
            List of KeywordSuggestion objects
        """
        cache_key = f"{keyword}_{self.language}_{self.region}"
        
        # Check cache
        if use_cache:
            cached = cache.get("autocomplete", cache_key)
            if cached:
                return [KeywordSuggestion(**s) for s in cached]
        
        # Fetch fresh
        raw_suggestions = self._fetch_suggestions(keyword)
        
        suggestions = [
            KeywordSuggestion(
                keyword=suggestion,
                position=i + 1,
                source="youtube_autocomplete"
            )
            for i, suggestion in enumerate(raw_suggestions)
        ]
        
        # Cache results
        if suggestions:
            cache.set("autocomplete", cache_key, [
                {"keyword": s.keyword, "position": s.position, "source": s.source}
                for s in suggestions
            ])
        
        return suggestions
    
    def expand_suggestions(
        self,
        keyword: str,
        prefixes: bool = True,
        suffixes: bool = True,
        alphabet: str = "abcdefghijklmnopqrstuvwxyz",
        numbers: bool = True,
        use_cache: bool = True
    ) -> list[KeywordSuggestion]:
        """
        Expand keyword with prefix/suffix to find more long-tail keywords.
        
        Args:
            keyword: The seed keyword
            prefixes: Add letters before the keyword
            suffixes: Add letters after the keyword
            alphabet: Characters to use for expansion
            numbers: Also use numbers 0-9
            use_cache: Whether to use cached results
            
        Returns:
            Combined list of all suggestions (deduplicated)
        """
        all_suggestions: dict[str, KeywordSuggestion] = {}
        
        # Characters to use
        chars = list(alphabet)
        if numbers:
            chars.extend([str(i) for i in range(10)])
        
        # Base suggestions
        for s in self.get_suggestions(keyword, use_cache):
            all_suggestions[s.keyword.lower()] = s
        
        # Suffix expansion: "keyword a", "keyword b", etc.
        if suffixes:
            for char in chars:
                query = f"{keyword} {char}"
                for s in self.get_suggestions(query, use_cache):
                    key = s.keyword.lower()
                    if key not in all_suggestions:
                        all_suggestions[key] = s
        
        # Prefix expansion: "a keyword", "b keyword", etc.
        if prefixes:
            for char in chars:
                query = f"{char} {keyword}"
                for s in self.get_suggestions(query, use_cache):
                    key = s.keyword.lower()
                    if key not in all_suggestions:
                        all_suggestions[key] = s
        
        # Question expansions
        question_words = ["how to", "what is", "why", "best", "top"]
        for qw in question_words:
            query = f"{qw} {keyword}"
            for s in self.get_suggestions(query, use_cache):
                key = s.keyword.lower()
                if key not in all_suggestions:
                    all_suggestions[key] = s
        
        return list(all_suggestions.values())
    
    def get_related_searches(
        self,
        keyword: str,
        depth: int = 1,
        use_cache: bool = True
    ) -> list[KeywordSuggestion]:
        """
        Recursively get related searches.
        
        Args:
            keyword: The seed keyword
            depth: How many levels deep to go (1 = just direct suggestions)
            use_cache: Whether to use cached results
            
        Returns:
            All discovered keywords
        """
        discovered: dict[str, KeywordSuggestion] = {}
        to_process = [keyword]
        processed = set()
        
        for _ in range(depth):
            next_batch = []
            
            for kw in to_process:
                if kw in processed:
                    continue
                processed.add(kw)
                
                suggestions = self.get_suggestions(kw, use_cache)
                for s in suggestions:
                    key = s.keyword.lower()
                    if key not in discovered and key != keyword.lower():
                        discovered[key] = s
                        next_batch.append(s.keyword)
            
            to_process = next_batch[:MAX_RELATED_SEARCHES_PER_BATCH]  # Limit to prevent explosion
        
        return list(discovered.values())


# Convenience function
def scrape_autocomplete(
    keyword: str,
    expand: bool = False,
    language: str = "en",
    region: str = "us"
) -> list[KeywordSuggestion]:
    """
    Convenience function to scrape autocomplete suggestions.
    
    Args:
        keyword: The seed keyword
        expand: Whether to do prefix/suffix expansion
        language: Language code (e.g., 'en', 'de')
        region: Region code (e.g., 'us', 'de')
        
    Returns:
        List of keyword suggestions
    """
    scraper = AutocompleteScraper(language=language, region=region)
    
    if expand:
        return scraper.expand_suggestions(keyword)
    return scraper.get_suggestions(keyword)
