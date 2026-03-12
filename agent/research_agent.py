"""
LangGraph-based Research Agent.

Graph topology:
  START → plan_queries → search → scrape → synthesize → END
"""

import logging
from typing import Annotated, Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

from config.settings import settings
from utils.scraper import scrape_multiple
from utils.search import format_search_context, search_web

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    topic: str
    queries: list[str]
    search_results: list[dict]
    scraped_sources: list[dict]
    context: str
    answer: str
    sources: list[dict]
    error: str | None
    status_log: Annotated[list[str], lambda a, b: a + b]


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _get_llm(temperature: float = 0.2) -> ChatGroq:
    """Full quality model for synthesis."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        max_tokens=1024,  # ✅ reduced from 2048
    )

def _get_fast_llm(temperature: float = 0.2) -> ChatGroq:
    """Fast model for query planning."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=temperature,
        max_tokens=512,
    )


# ---------------------------------------------------------------------------
# Node: plan_queries
# ---------------------------------------------------------------------------

PLANNER_SYSTEM = """You are a research query planner. Given a research topic, generate

Rules:
- Output ONLY a numbered list of queries, one per line (e.g. "1. query here")
- No intro text, no explanations, no extra formatting
- Queries should cover different angles: overview, recent developments, key facts, comparisons
- Keep queries concise (under 10 words each)
"""


def plan_queries(state: AgentState) -> dict:
    topic = state["topic"]
    logger.info("Planning queries for: %s", topic)

    try:
        llm = _get_fast_llm(temperature=0.3)
        response = llm.invoke([
            SystemMessage(content=PLANNER_SYSTEM),
            HumanMessage(content=f"Research topic: {topic}"),
        ])

        lines = response.content.strip().split("\n")
        queries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            import re
            cleaned = re.sub(r"^[\d\-\*\.\)]+\s*", "", line).strip()
            if cleaned:
                queries.append(cleaned)

        if topic not in queries:
            queries.insert(0, topic)

        queries = queries[:5]
        logger.info("Generated %d queries", len(queries))
        return {
            "queries": queries,
            "status_log": [f"📋 Generated {len(queries)} search queries"],
        }

    except Exception as e:
        logger.error("plan_queries failed: %s", e)
        return {
            "queries": [topic],
            "status_log": [f"⚠️ Query planning failed, using topic directly: {e}"],
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Node: search
# ---------------------------------------------------------------------------

def search(state: AgentState) -> dict:
    queries = state["queries"]
    all_results: list[dict] = []
    seen_urls: set[str] = set()

    for query in queries:
        logger.info("Searching: %s", query)
        results = search_web(query, max_results=settings.MAX_SEARCH_RESULTS)
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)

    logger.info("Total unique search results: %d", len(all_results))
    return {
        "search_results": all_results,
        "status_log": [f"🔍 Found {len(all_results)} unique sources across {len(queries)} queries"],
    }


# ---------------------------------------------------------------------------
# Node: scrape
# ---------------------------------------------------------------------------

def scrape(state: AgentState) -> dict:
    results = state["search_results"]
    urls = [r["url"] for r in results if r.get("url")]
    urls_to_scrape = urls[:8]

    logger.info("Scraping %d URLs", len(urls_to_scrape))
    scraped = scrape_multiple(urls_to_scrape, max_chars=settings.MAX_SCRAPE_CHARS)

    context = format_search_context(results, scraped)

    sources = []
    scraped_map = {s["url"]: s for s in scraped}
    for r in results[:8]:
        url = r.get("url", "")
        scraped_data = scraped_map.get(url, {})
        sources.append({
            "title": scraped_data.get("title") or r.get("title", "Untitled"),
            "url": url,
            "snippet": r.get("snippet", ""),
            "scraped": bool(scraped_data.get("content")),
        })

    return {
        "scraped_sources": scraped,
        "context": context,
        "sources": sources,
        "status_log": [f"📄 Successfully scraped {len(scraped)} pages"],
    }


# ---------------------------------------------------------------------------
# Node: synthesize
# ---------------------------------------------------------------------------

# ✅ Tightened prompt for faster, more focused output
SYNTHESIZER_SYSTEM = """You are an expert research analyst. Synthesize the provided sources into a clear, concise report.

Guidelines:
- Write in a clear, informative tone
- Structure: brief introduction, key findings, conclusion
- Use **bold** for important terms or key points
- Cite sources inline using [Source N] notation
- Do NOT fabricate information not present in the sources
- Aim for 250-400 words maximum
- End with a "Key Takeaways" section with 3-5 bullet points starting with •
"""


def synthesize(state: AgentState) -> dict:
    topic = state["topic"]
    context = state["context"]

    if not context.strip():
        return {
            "answer": "I was unable to gather sufficient information from the web to answer this query.",
            "status_log": ["❌ No content available for synthesis"],
        }

    logger.info("Synthesizing answer for: %s", topic)

    try:
        llm = _get_llm(temperature=0.4)
        prompt = f"""Research Topic: {topic}

Source Material:
{context}

Please provide a comprehensive, well-structured research summary based on the sources above.
IMPORTANT: Only cite sources numbered [Source 1] through [Source {len(state['sources'])}]. Never hallucinate source numbers beyond what is provided."""

        response = llm.invoke([
            SystemMessage(content=SYNTHESIZER_SYSTEM),
            HumanMessage(content=prompt),
        ])

        answer = response.content.strip()
        return {
            "answer": answer,
            "status_log": ["✅ Research synthesis complete"],
        }

    except Exception as e:
        logger.error("synthesize failed: %s", e)
        return {
            "answer": f"Synthesis failed due to an error: {e}",
            "status_log": [f"❌ Synthesis error: {e}"],
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph() -> Any:
    builder = StateGraph(AgentState)

    builder.add_node("plan_queries", plan_queries)
    builder.add_node("search", search)
    builder.add_node("scrape", scrape)
    builder.add_node("synthesize", synthesize)

    builder.add_edge(START, "plan_queries")
    builder.add_edge("plan_queries", "search")
    builder.add_edge("search", "scrape")
    builder.add_edge("scrape", "synthesize")
    builder.add_edge("synthesize", END)

    return builder.compile()


research_graph = build_graph()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_research(topic: str) -> AgentState:
    initial_state: AgentState = {
        "topic": topic,
        "queries": [],
        "search_results": [],
        "scraped_sources": [],
        "context": "",
        "answer": "",
        "sources": [],
        "error": None,
        "status_log": [f"🚀 Starting research on: {topic}"],
    }

    final_state = research_graph.invoke(initial_state)
    return final_state
