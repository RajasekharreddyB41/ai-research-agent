"""
Web scraping utilities using BeautifulSoup.
Handles fetching, cleaning, and extracting text from web pages.
"""

import logging
import re
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

BLOCKED_DOMAINS = {
    "twitter.com", "x.com", "facebook.com", "instagram.com",
    "linkedin.com", "reddit.com", "tiktok.com", "youtube.com",
}


def _is_scrapable(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.lower().lstrip("www.")
        return domain not in BLOCKED_DOMAINS
    except Exception:
        return False


def _clean_text(text: str) -> str:
    """Collapse whitespace and strip boilerplate noise."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def scrape_url(url: str, max_chars: Optional[int] = None) -> dict:
    """
    Fetch a URL and return extracted text content.

    Returns:
        dict with keys: url, title, content, error (optional)
    """
    max_chars = max_chars or settings.MAX_SCRAPE_CHARS

    if not _is_scrapable(url):
        return {"url": url, "title": "", "content": "", "error": "Domain blocked for scraping"}

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=settings.REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "text/plain" not in content_type:
            return {"url": url, "title": "", "content": "", "error": f"Unsupported content-type: {content_type}"}

        soup = BeautifulSoup(response.text, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        main = soup.find("article") or soup.find("main") or soup.find("body")
        raw_text = main.get_text(separator=" ") if main else soup.get_text(separator=" ")

        content = _clean_text(raw_text)[:max_chars]

        return {"url": url, "title": title, "content": content, "error": None}

    except requests.exceptions.Timeout:
        logger.warning("Timeout scraping %s", url)
        return {"url": url, "title": "", "content": "", "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        logger.warning("Request error scraping %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "error": str(e)}
    except Exception as e:
        logger.error("Unexpected error scraping %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "error": str(e)}


def scrape_multiple(urls: list[str], max_chars: Optional[int] = None) -> list[dict]:
    """Scrape multiple URLs in parallel for speed."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from config.settings import settings

    results = []
    max_workers = settings.MAX_SCRAPE_WORKERS

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(scrape_url, url, max_chars): url
            for url in urls
        }
        for future in as_completed(future_to_url):
            try:
                result = future.result()
                if result["content"]:
                    results.append(result)
                else:
                    logger.info("Skipping %s: %s", future_to_url[future], result.get("error"))
            except Exception as e:
                logger.error("Scrape thread error: %s", e)

    return results
