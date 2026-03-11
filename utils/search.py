"""
Web search utilities using DuckDuckGo Search API.
Returns structured search results with URL, title, and snippet.
"""

import logging
import time
from typing import Optional

from duckduckgo_search import DDGS

from config.settings import settings

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: Optional[int] = None) -> list[dict]:
    """
    Search the web using DuckDuckGo with retry logic.
    """
    max_results = max_results or settings.MAX_SEARCH_RESULTS
    results = []

    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(
                    query,
                    max_results=max_results,
                    safesearch="off",
                    timelimit="y",
                ))

            for item in raw:
                url = item.get("href", "")
                if url:
                    results.append({
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("body", ""),
                    })

            if results:
                logger.info("Search '%s' returned %d results", query, len(results))
                return results

            logger.warning("Attempt %d: no results for '%s'", attempt + 1, query)
            time.sleep(2)

        except Exception as e:
            logger.error("Attempt %d failed for '%s': %s", attempt + 1, query, e)
            time.sleep(3)

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

        body = full_content if full_content else snippet
        sections.append(
            f"[Source {i}]\nTitle: {title}\nURL: {url}\nContent:\n{body}"
        )

    return "\n\n---\n\n".join(sections)
