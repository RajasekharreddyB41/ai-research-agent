def search_web(query: str, max_results: Optional[int] = None) -> list[dict]:
    """
    Search the web using DuckDuckGo with retry logic.
    """
    import time
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