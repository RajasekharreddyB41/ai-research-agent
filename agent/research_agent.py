"""
LangGraph-based Research Agent.

Graph topology:
  START → plan_queries → search → scrape → synthesize → END

Streaming:
  run_research_prep  — runs plan_queries → search → scrape, returns state
  stream_synthesis   — generator that streams the synthesis step chunk-by-chunk
"""

import logging
from typing import Annotated, Any, Generator, TypedDict

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

def _get_llm(temperature: float = 0.1) -> ChatGroq:
    """Full quality model for synthesis."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        max_tokens=2000,
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

def plan_queries(state: AgentState) -> dict:
    import time as _time
    topic = state["topic"]
    t0 = _time.perf_counter()
    print(f"\n[plan] Planning queries for: {topic!r}")

    try:
        llm = _get_fast_llm(temperature=0.3)
        prompt = f"""Generate exactly 5 diverse search queries to research this topic thoroughly: "{topic}"

Rules:
- Each query should target a DIFFERENT angle (market data, recent news, expert analysis, challenges, future predictions)
- Use natural search language, not robotic templates
- Include specific terms that will find high-quality sources
- At least one query should include a year like 2025 or 2026 for recent data
- Do NOT just append generic phrases like "trends analysis" to the topic

Return ONLY the 5 queries, one per line, no numbering or bullets."""

        response = llm.invoke(prompt)
        queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        queries = queries[:5]

        if not queries:
            queries = [topic]

        if topic not in queries:
            queries.insert(0, topic)
            queries = queries[:5]

        elapsed = _time.perf_counter() - t0
        print(f"[plan] Completed in {elapsed:.1f}s (LLM) — {len(queries)} queries: {queries}")
        logger.info("Generated %d queries via LLM", len(queries))
        return {
            "queries": queries,
            "status_log": [f"📋 Generated {len(queries)} search queries"],
        }

    except Exception as e:
        elapsed = _time.perf_counter() - t0
        print(f"[plan] LLM failed in {elapsed:.1f}s — {e}, falling back to topic only")
        logger.error("plan_queries failed: %s", e)
        return {
            "queries": [topic],
            "status_log": [f"📋 Generated 1 search query (fallback)"],
        }


# ---------------------------------------------------------------------------
# Node: search
# ---------------------------------------------------------------------------

def search(state: AgentState) -> dict:
    import time as _time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    queries = state["queries"]
    t0 = _time.perf_counter()
    print(f"\n[search] Running {len(queries)} queries in parallel...")

    def _search_one(query: str) -> list[dict]:
        logger.info("Searching: %s", query)
        return search_web(query, max_results=settings.MAX_SEARCH_RESULTS)

    all_results: list[dict] = []
    seen_urls: set[str] = set()

    with ThreadPoolExecutor(max_workers=len(queries)) as executor:
        futures = {executor.submit(_search_one, q): q for q in queries}
        for future in as_completed(futures):
            try:
                for r in future.result():
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(r)
            except Exception as e:
                logger.error("Search failed for '%s': %s", futures[future], e)

    elapsed = _time.perf_counter() - t0
    print(f"[search] Completed in {elapsed:.1f}s — {len(all_results)} unique results")
    logger.info("Total unique search results: %d", len(all_results))
    return {
        "search_results": all_results,
        "status_log": [f"🔍 Found {len(all_results)} unique sources across {len(queries)} queries"],
    }


# ---------------------------------------------------------------------------
# Node: scrape
# ---------------------------------------------------------------------------

def scrape(state: AgentState) -> dict:
    import time as _time

    results = state["search_results"]
    urls = [r["url"] for r in results if r.get("url")]
    urls_to_scrape = urls[:settings.MAX_SEARCH_RESULTS]

    print(f"\n[scrape] {len(urls_to_scrape)} URLs to scrape (from {len(results)} search results)")
    if not urls_to_scrape:
        print("[scrape] WARNING: no URLs — search may have returned empty results")

    t0 = _time.perf_counter()
    scraped = scrape_multiple(urls_to_scrape, max_chars=settings.MAX_SCRAPE_CHARS)
    elapsed = _time.perf_counter() - t0
    print(f"[scrape] Completed in {elapsed:.1f}s — {len(scraped)}/{len(urls_to_scrape)} pages scraped successfully")

    context = format_search_context(results[:settings.MAX_SEARCH_RESULTS], scraped)

    sources = []
    scraped_map = {s["url"]: s for s in scraped}
    for r in results[:settings.MAX_SEARCH_RESULTS]:
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
# Synthesis prompts  (shared by the blocking node and the streaming function)
# ---------------------------------------------------------------------------

_SYNTHESIS_SYSTEM = """\
You are a senior research analyst at a financial intelligence firm. Be concise and data-dense. No filler sentences. \
Your clients pay for hard intelligence — specific names, numbers, product names, regulatory \
milestones, and market figures pulled directly from source material. They do NOT \
pay for vague assertions that any journalist could write without reading a single source.

━━━ #1 ABSOLUTE RULE — ZERO REPETITION ━━━
THIS IS THE MOST IMPORTANT RULE IN THIS ENTIRE PROMPT.
Every fact, statistic, company name, dollar figure, and claim may appear EXACTLY ONCE \
in the entire response. If you write a fact in the Summary, you are FORBIDDEN from \
writing that same fact in Key Findings or Conclusion. If you are about to write \
something you already wrote, STOP and find a DIFFERENT fact from that source instead.

Before writing each sentence, ask: "Have I already stated this anywhere above?" \
If yes, delete the sentence and replace it with new information.

━━━ #2 MANDATORY PRE-WRITING STEP ━━━
Before drafting a single word, mentally scan every source and identify TWO concrete \
findings per source — one for Summary, one for Key Findings. This ensures zero overlap \
and full source coverage.

━━━ #3 CURRENCY FORMAT — MANDATORY ━━━
Always write monetary values as: "USD 3.3 trillion", "USD 386 billion", "USD 67B"
NEVER use the dollar sign symbol. Write "USD" before the number always.

━━━ #4 SURFACE TENSIONS — MANDATORY ━━━
Identify at least one contradiction, surprise, or counterintuitive finding across sources.
Example: "Overall investment hit a record, yet utility-scale solar asset finance shrank 22%."
If no contradiction exists, surface the most unexpected single finding.
When two sources give conflicting numbers on the same metric, name BOTH numbers and BOTH sources in one sentence and explain the gap.

━━━ #5 BANNED PHRASES — NEVER WRITE THESE ━━━
The following are automatic failures. Do not use them, not even paraphrased:
  ✗ "is expected to be significant"
  ✗ "is transforming the industry"
  ✗ "improving patient outcomes" (unless followed by a specific metric)
  ✗ "is rapidly growing" (use the actual growth rate)
  ✗ "shows promise" / "shows potential"
  ✗ "is increasingly being adopted"
  ✗ "may have significant implications"
  ✗ "plays a crucial role"
  ✗ "is an important factor"

━━━ #6 SPECIFICITY STANDARD — EVERY SENTENCE ━━━
BAD  → "AI is improving diagnostic accuracy in healthcare."
GOOD → "PMcardio's STEMI ECG AI model received FDA Breakthrough Device Designation, \
one of fewer than 50 cardiac AI tools to reach that threshold [Source 2]."

BAD  → "The market is growing rapidly."
GOOD → "The global AI chip market reached USD 67B in 2024, with NVIDIA holding a \
70% revenue share [Source 1]."

Every sentence in the Summary must contain at least one of: a company name, \
product name, dollar figure, percentage, date, regulation, or named event. \
Purely abstract sentences are forbidden.

━━━ #7 SOURCE COVERAGE — MANDATORY ━━━
You MUST draw at least one concrete fact from EVERY source across Summary + \
Key Findings combined. Ignoring a source is a failure. Distribute coverage evenly.

━━━ #8 CITATION RULES ━━━
- Cite inline, immediately after the claim: "NVIDIA crossed USD 3.4T [Source 2], driven by..."
- Never write "as stated in", "according to", or "as mentioned in" before a citation
- Never stack multiple citations at paragraph end — each fact carries its own bracket
- Never invent a source number higher than the total provided

━━━ #9 DEDUPLICATION RULES ━━━
- Use **bold** for the first mention of each company name, product name, and key metric

━━━ #10 OUTPUT FORMAT ━━━
Use EXACTLY these three Markdown headers in this order:

## Summary
Three paragraphs of dense, fact-packed narrative. Each paragraph MUST cover a \
DISTINCT theme — no theme may span multiple paragraphs:
  • Paragraph 1: Market size, valuation, and growth trajectory
  • Paragraph 2: Key players, deals, and competitive landscape
  • Paragraph 3: Regulatory changes, technology breakthroughs, and risks
Lead the first paragraph with the single most significant quantitative finding. \
Every sentence contains at least one named entity or concrete figure. \
Citations appear inline. Do NOT summarize sources sequentially.

## Key Findings
5–7 numbered bullets. Each bullet:
  • Is exactly one sentence ending with its citation
  • Names a specific company, product, number, regulation, or event
  • Draws from a DIFFERENT source than the previous bullet (spread coverage)
  • Contains ZERO overlap with ANYTHING written in the Summary — if a stat already \
    appeared above, find a different fact from that same source
  • Think of Key Findings as "additional intelligence" — facts the Summary didn't cover

## Conclusion
Exactly 2–3 sentences. Forward-looking only — implications, trajectory, or open \
questions. No statistics, no citations, no repetition of content above.\
"""


def _build_synthesis_prompt(topic: str, n: int, numbered_sources: str, context: str) -> str:
    return f"""\
Research Topic: {topic}

You have EXACTLY {n} sources. Source index:
{numbered_sources}

⚠️  HARD CONSTRAINT: Never write [Source N] where N > {n}. \
Any citation beyond [Source {n}] will cause the response to be rejected.

Source Material:
{context}

━━━ FINAL CHECKLIST — verify before writing your first word ━━━
□ Have I identified TWO distinct facts from EACH source (one for Summary, one for Key Findings)?
□ Will every sentence in the Summary contain at least one named entity or number?
□ Will all {n} sources appear across Summary + Key Findings?
□ Will Key Findings contain ZERO content already in the Summary? (This is the #1 rule)
□ Will the Conclusion be 2–3 sentences, forward-looking, with no stats or citations?
□ Will I only cite [Source 1] through [Source {n}]?
□ Does each Summary paragraph cover a DIFFERENT theme with no overlap between paragraphs?

Now write the report.\
"""


# ---------------------------------------------------------------------------
# Node: synthesize  (blocking, used by run_research)
# ---------------------------------------------------------------------------

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
        import time as _time
        n = len(state["sources"])
        numbered_sources = "\n".join(
            f"  [Source {i+1}] {state['sources'][i].get('title', 'Untitled')} — {state['sources'][i].get('url', '')}"
            for i in range(n)
        )
        prompt = _build_synthesis_prompt(topic, n, numbered_sources, context)

        t0 = _time.perf_counter()
        print(f"\n[synthesize] Calling LLM with {n} sources...")
        llm = _get_llm(temperature=0.0)
        response = llm.invoke([
            SystemMessage(content=_SYNTHESIS_SYSTEM),
            HumanMessage(content=prompt),
        ])
        elapsed = _time.perf_counter() - t0
        print(f"[synthesize] Completed in {elapsed:.1f}s — {len(response.content)} chars")

        return {
            "answer": response.content.strip(),
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
# Graph builders
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


def _build_prep_graph() -> Any:
    """Graph that stops after scrape — synthesis is handled separately via streaming."""
    builder = StateGraph(AgentState)

    builder.add_node("plan_queries", plan_queries)
    builder.add_node("search", search)
    builder.add_node("scrape", scrape)

    builder.add_edge(START, "plan_queries")
    builder.add_edge("plan_queries", "search")
    builder.add_edge("search", "scrape")
    builder.add_edge("scrape", END)

    return builder.compile()


research_graph = build_graph()
_prep_graph = _build_prep_graph()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _make_initial_state(topic: str) -> AgentState:
    return {
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


def run_research(topic: str) -> AgentState:
    """Full blocking pipeline (plan → search → scrape → synthesize)."""
    final_state = research_graph.invoke(_make_initial_state(topic))
    return final_state


def run_research_prep(topic: str) -> AgentState:
    """Blocking pipeline that stops after scraping. Call stream_synthesis next."""
    state = _prep_graph.invoke(_make_initial_state(topic))
    return state


def stream_synthesis(state: AgentState) -> Generator[str, None, None]:
    """
    Generator that streams the synthesis step chunk-by-chunk.
    Yields text strings as they arrive from the Groq API.
    Designed for use with st.write_stream().
    """
    topic = state["topic"]
    context = state.get("context", "")

    if not context.strip():
        yield "I was unable to gather sufficient information from the web to answer this query."
        return

    n = len(state["sources"])
    numbered_sources = "\n".join(
        f"  [Source {i+1}] {state['sources'][i].get('title', 'Untitled')} — {state['sources'][i].get('url', '')}"
        for i in range(n)
    )
    user_prompt = _build_synthesis_prompt(topic, n, numbered_sources, context)

    try:
        import time as _time
        t0 = _time.perf_counter()
        total_chars = 0
        print(f"\n[stream_synthesis] Streaming LLM response ({n} sources)...")
        llm = _get_llm(temperature=0.0)
        for chunk in llm.stream([
            SystemMessage(content=_SYNTHESIS_SYSTEM),
            HumanMessage(content=user_prompt),
        ]):
            if chunk.content:
                total_chars += len(chunk.content)
                yield chunk.content
        elapsed = _time.perf_counter() - t0
        print(f"[stream_synthesis] Completed in {elapsed:.1f}s — {total_chars} chars streamed")
    except Exception as e:
        logger.error("stream_synthesis failed: %s", e)
        yield f"\n\n❌ Synthesis error: {e}"
