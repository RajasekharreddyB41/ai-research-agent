"""
Web search utilities using Tavily Search API.
Returns structured search results with URL, title, and snippet.
"""

import logging
import os
import re
from typing import Optional

import requests

from config.settings import settings

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_URL = "https://api.tavily.com/search"


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode common entities."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&[a-zA-Z]{2,6};", " ", text)
    text = re.sub(r"&#?\w+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def search_web(query: str, max_results: Optional[int] = None) -> list[dict]:
    """
    Search the web using Tavily API.
    """
    max_results = max_results or settings.MAX_SEARCH_RESULTS
    results = []

    if not TAVILY_API_KEY:
        logger.error("TAVILY_API_KEY is not set")
        return []

    try:
        response = requests.post(
            TAVILY_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("results", []):
            url = item.get("url", "")
            if url:
                results.append({
                    "title": _strip_html(item.get("title", "")),
                    "url": url,
                    "snippet": _strip_html(item.get("content", "")),
                })

        logger.info("Tavily search '%s' returned %d results", query, len(results))
        return results

    except Exception as e:
        logger.error("Tavily search failed for '%s': %s", query, e)
        return []


def format_search_context(results: list[dict], scraped: list[dict]) -> str:
    """
    Build a structured context string from search results + scraped content
    to pass to the LLM for synthesis.
    """
    sections = []
    scraped_map = {s["url"]: s for s in scraped}

    for i, result in enumerate(results, 1):
        url = result.get("url", "")
        title = result.get("title", "No title")
        snippet = result.get("snippet", "")
        scraped_data = scraped_map.get(url, {})
        full_content = scraped_data.get("content", "")

        # ✅ Limit body to 1500 chars to reduce LLM input size → faster synthesis
        body = _strip_html(full_content if full_content else snippet)[:1500]
        sections.append(
            f"[Source {i}]\nTitle: {title}\nURL: {url}\nContent:\n{body}"
        )

    return "\n\n---\n\n".join(sections)
