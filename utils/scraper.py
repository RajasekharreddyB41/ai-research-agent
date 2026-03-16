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

# Content-types that are definitely not parseable as HTML — reject these only
_BINARY_TYPES = ("application/pdf", "application/zip", "image/", "video/", "audio/")

# Tags always stripped before extraction
_NOISE_TAGS = [
    "script", "style", "noscript", "nav", "header", "footer",
    "aside", "form", "iframe", "svg", "figure",
]

# CSS selectors for elements that are noise regardless of tag name.
# Ordered from most to least specific — decomposed before content extraction.
_NOISE_SELECTORS = [
    '[role="navigation"]',
    '[role="complementary"]',
    '[role="banner"]',
    '[role="contentinfo"]',
    '[class*="sidebar"]',   '[id*="sidebar"]',
    '[class*="breadcrumb"]',
    '[class*="social-share"]', '[class*="share-button"]',
    '[class*="related-post"]', '[class*="related-article"]',
    '[class*="newsletter"]',   '[class*="subscription"]',
    '[class*="advertisement"]','[class*="cookie-banner"]',
    '[class*="cookie-notice"]','[id*="cookie"]',
    '[class*="popup"]',        '[class*="modal"]',
]

# Content selectors tried in priority order.
# For each selector all matches are evaluated; the longest text wins.
# First selector that yields ≥200 chars is used — so semantic tags
# (article, main) take priority over class-based ones.
_CONTENT_SELECTORS = [
    "article",
    "main",
    '[role="main"]',
    '[itemprop="articleBody"]',
    # Common CMS / blogging patterns
    '[class*="article-body"]',   '[class*="article_body"]',
    '[class*="post-content"]',   '[class*="post_content"]',
    '[class*="entry-content"]',  '[class*="entry_content"]',
    '[class*="story-body"]',     '[class*="story_body"]',
    '[class*="article-content"]','[class*="article_content"]',
    '[class*="content-body"]',   '[class*="content_body"]',
    '[class*="main-content"]',   '[class*="main_content"]',
    '[class*="page-content"]',   '[class*="page_content"]',
    '[class*="prose"]',
    "#content", "#main", "#article", "#primary",
]


def _is_scrapable(url: str) -> bool:
    try:
        netloc = urlparse(url).netloc.lower()
        # removeprefix is correct — lstrip("www.") strips individual chars, not the prefix
        domain = netloc.removeprefix("www.")
        return domain not in BLOCKED_DOMAINS
    except Exception:
        return False


def _clean_text(text: str) -> str:
    """Collapse whitespace and strip boilerplate noise."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_main_content(soup: BeautifulSoup) -> str:
    """
    Return the best-guess article body text from a cleaned soup tree.

    Strategy:
    1. Try each selector in _CONTENT_SELECTORS in order.
       For each, collect all matching elements and take the longest text.
       Accept the first selector that yields ≥200 chars of text.
    2. Fall back to <body> if nothing substantial is found.
    """
    for selector in _CONTENT_SELECTORS:
        candidates = soup.select(selector)
        if not candidates:
            continue
        # Among all elements matching this selector, pick the longest
        texts = [_clean_text(el.get_text(separator=" ")) for el in candidates]
        best = max(texts, key=len)
        if len(best) >= 200:
            return best

    # Fallback: full body text
    body = soup.find("body")
    if body:
        return _clean_text(body.get_text(separator=" "))
    return _clean_text(soup.get_text(separator=" "))


def scrape_url(url: str, max_chars: Optional[int] = None) -> dict:
    """
    Fetch a URL and return extracted text content.

    Returns:
        dict with keys: url, title, content, error (optional)
    """
    max_chars = max_chars or settings.MAX_SCRAPE_CHARS

    if not _is_scrapable(url):
        print(f"[scraper] BLOCKED  {url}")
        return {"url": url, "title": "", "content": "", "error": "Domain blocked for scraping"}

    print(f"[scraper] TRYING   {url}")
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=(2, 4),
            allow_redirects=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")

        # Only reject if clearly binary — attempt to parse everything else as HTML
        if any(content_type.startswith(t) for t in _BINARY_TYPES):
            print(f"[scraper] SKIP     {url}  (content-type: {content_type})")
            return {"url": url, "title": "", "content": "", "error": f"Unsupported content-type: {content_type}"}

        soup = BeautifulSoup(response.text, "lxml")

        # Strip noise tags first
        for tag in soup(_NOISE_TAGS):
            tag.decompose()

        # Strip noise elements by role/class pattern
        for selector in _NOISE_SELECTORS:
            for el in soup.select(selector):
                el.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        content = _extract_main_content(soup)[:max_chars]

        if content:
            print(f"[scraper] OK       {url}  ({len(content)} chars)")
        else:
            print(f"[scraper] EMPTY    {url}  (parsed but no content extracted)")

        return {"url": url, "title": title, "content": content, "error": None}

    except requests.exceptions.Timeout:
        print(f"[scraper] TIMEOUT  {url}")
        logger.warning("Timeout scraping %s", url)
        return {"url": url, "title": "", "content": "", "error": "Request timed out"}
    except requests.exceptions.ConnectionError as e:
        print(f"[scraper] CONN ERR {url}  ({e})")
        logger.warning("Connection error scraping %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "error": str(e)}
    except requests.exceptions.HTTPError as e:
        print(f"[scraper] HTTP {e.response.status_code}  {url}")
        logger.warning("HTTP error scraping %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "error": str(e)}
    except requests.exceptions.RequestException as e:
        print(f"[scraper] REQ ERR  {url}  ({e})")
        logger.warning("Request error scraping %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "error": str(e)}
    except Exception as e:
        print(f"[scraper] ERROR    {url}  ({type(e).__name__}: {e})")
        logger.error("Unexpected error scraping %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "error": str(e)}


def scrape_multiple(urls: list[str], max_chars: Optional[int] = None) -> list[dict]:
    """Scrape multiple URLs in parallel for speed."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from config.settings import settings

    print(f"\n[scraper] ── scrape_multiple: {len(urls)} URLs, max_workers={settings.MAX_SCRAPE_WORKERS} ──")
    for i, u in enumerate(urls, 1):
        print(f"[scraper]   {i}. {u}")

    results = []
    skipped = []
    max_workers = settings.MAX_SCRAPE_WORKERS

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(scrape_url, url, max_chars): url
            for url in urls
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result["content"]:
                    results.append(result)
                else:
                    skipped.append((url, result.get("error", "empty content")))
                    logger.info("Skipping %s: %s", url, result.get("error"))
            except Exception as e:
                skipped.append((url, str(e)))
                logger.error("Scrape thread error for %s: %s", url, e)

    print(f"[scraper] ── DONE: {len(results)} succeeded, {len(skipped)} failed/empty ──")
    if skipped:
        print("[scraper] Failed URLs:")
        for u, reason in skipped:
            print(f"[scraper]   FAIL  {u}  → {reason}")
    print()
    return results
