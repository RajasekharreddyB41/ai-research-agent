"""
AI Research Agent — Recruiter-Level Professional UI
Clean white + dark blue design with agent workflow visualization.
"""

import logging
import sys
import time
import re
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import settings  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f8fafc !important;
    color: #1e293b !important;
}
.stApp { background: #f8fafc !important; }
.block-container { padding: 0 2rem 3rem !important; max-width: 900px !important; }

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #60a5fa;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero h1 { font-size: 2.6rem; font-weight: 700; color: #f1f5f9; margin: 0.5rem 0; letter-spacing: -0.5px; }
.hero h1 span { color: #3b82f6; }
.hero p { color: #94a3b8; font-size: 1rem; margin: 0.8rem auto 0; max-width: 500px; line-height: 1.6; }

.search-container {
    background: white;
    border-radius: 12px;
    padding: 1.8rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
    border: 1px solid #e2e8f0;
}
.search-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.stTextArea textarea {
    background: #f8fafc !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 8px !important;
    color: #1e293b !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.9rem 1.1rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
.stTextArea textarea::placeholder { color: #94a3b8 !important; }

.stButton > button {
    background: #1e40af !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #1d4ed8 !important;
    box-shadow: 0 4px 15px rgba(29,78,216,0.3) !important;
}

.workflow-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    border: 1px solid #e2e8f0;
}
.workflow-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.workflow-steps {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.workflow-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    flex: 1;
    min-width: 120px;
    justify-content: center;
}
.step-pending { background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; }
.step-active  { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
.step-done    { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.workflow-arrow { color: #cbd5e1; font-size: 1.2rem; flex-shrink: 0; }

.agent-log {
    background: #0f172a;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
}
.log-line       { color: #64748b; }
.log-line.active { color: #38bdf8; }
.log-line.done  { color: #4ade80; }
.log-line.error { color: #f87171; }

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    background: white;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid #e2e8f0;
}
.metric-number { font-size: 2rem; font-weight: 700; color: #1e40af; line-height: 1; display: block; }
.metric-label  { font-size: 0.72rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; display: block; }

.results-section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin: 1.5rem 0;
    border: 1px solid #e2e8f0;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid #f1f5f9;
}
.summary-text { color: #334155; font-size: 0.95rem; line-height: 1.8; }
.summary-text strong { color: #1e40af; }

.insight-item {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.9rem;
    color: #334155;
    line-height: 1.5;
}
.insight-bullet {
    width: 6px;
    height: 6px;
    background: #3b82f6;
    border-radius: 50%;
    margin-top: 7px;
    flex-shrink: 0;
}

.source-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.7rem 0;
}
.source-card:hover { border-color: #3b82f6; }
.source-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}
.source-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #3b82f6;
    font-weight: 600;
    background: #eff6ff;
    padding: 2px 8px;
    border-radius: 4px;
}
.source-badge-full { font-size: 0.65rem; background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 4px; }
.source-badge-snip { font-size: 0.65rem; background: #fefce8; color: #ca8a04; border: 1px solid #fde68a; padding: 2px 8px; border-radius: 4px; }
.source-title   { font-size: 0.9rem; font-weight: 600; color: #1e293b; margin-bottom: 0.3rem; }
.source-url     { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #94a3b8; margin-bottom: 0.4rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.source-snippet { font-size: 0.82rem; color: #64748b; line-height: 1.5; }
.read-link      { display: inline-block; margin-top: 0.5rem; font-size: 0.78rem; color: #3b82f6; font-weight: 500; }

.query-tag {
    display: inline-block;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #2563eb;
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 3px;
    font-weight: 500;
}
.warn-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    color: #dc2626;
    font-size: 0.85rem;
    margin: 1rem 0;
}

section[data-testid="stSidebar"] { background: #0f172a !important; }
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 AI Research Agent")
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    for ex in [
        "AI chip market leaders 2026",
        "Future of electric vehicles",
        "AI in healthcare diagnostics",
        "Quantum computing breakthroughs",
        "Renewable energy investments",
    ]:
        st.markdown(f"• {ex}")
    st.markdown("---")
    st.markdown("### ⚙️ Model")
    st.markdown("`llama-3.3-70b-versatile`")
    st.markdown("---")
    st.markdown("### 📊 Settings")
    max_sources = st.slider("Max Sources", 3, 10, 5)
    max_chars = st.slider("Content Depth", 1000, 6000, 3000, step=500)
    st.markdown("---")
    st.markdown("### 🏗️ Pipeline")
    st.markdown("```\nQuery Planner\n     ↓\nWeb Search\n     ↓\nPage Scraper\n     ↓\nAI Synthesis\n```")
    st.caption("Built with LangGraph + Groq + Azure")


# ── Config check ──────────────────────────────────────────────────────────────
missing = settings.validate()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">LangGraph · Groq LLM · Azure App Service</div>
    <h1>AI Research <span>Agent</span></h1>
    <p>Ask complex research questions and get structured reports
    with real-time web sources, powered by autonomous AI agents.</p>
</div>
""", unsafe_allow_html=True)

if missing:
    st.markdown(
        f'<div class="warn-box">⚠️ Missing: <strong>{", ".join(missing)}</strong> — set in your .env file.</div>',
        unsafe_allow_html=True,
    )


# ── Search Input ──────────────────────────────────────────────────────────────
st.markdown('<div class="search-container"><div class="search-label">Research Question</div>', unsafe_allow_html=True)
topic = st.text_area(
    label="topic",
    placeholder="Research the impact of AI chips on data center infrastructure in 2026...",
    height=90,
    label_visibility="collapsed",
)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    research_clicked = st.button("🔍  Start Research", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def bold_to_html(text: str) -> str:
    """Convert **bold** markdown to <strong> HTML safely."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def render_workflow(step: int) -> str:
    """Render agent workflow steps. step: 0=idle, 1-4=active node, 5=done."""
    steps = [("🧠", "Query Planner"), ("🔍", "Web Search"), ("📄", "Page Scraper"), ("✨", "AI Synthesis")]
    html = '<div class="workflow-container"><div class="workflow-title">Agent Workflow</div><div class="workflow-steps">'
    for i, (icon, label) in enumerate(steps):
        node = i + 1
        if step == 0:
            cls = "step-pending"
        elif node < step:
            cls = "step-done"
            icon = "✅"
        elif node == step:
            cls = "step-active"
        else:
            cls = "step-pending"
        html += f'<div class="workflow-step {cls}">{icon} {label}</div>'
        if i < len(steps) - 1:
            html += '<div class="workflow-arrow">→</div>'
    return html + '</div></div>'


# ── Research Execution ────────────────────────────────────────────────────────
if research_clicked and topic.strip():
    if missing:
        st.error("Please set GROQ_API_KEY in your .env file.")
        st.stop()

    from agent.research_agent import run_research

    settings.MAX_SEARCH_RESULTS = max_sources
    settings.MAX_SCRAPE_CHARS = max_chars

    workflow_ph = st.empty()
    log_ph = st.empty()

    workflow_ph.markdown(render_workflow(1), unsafe_allow_html=True)
    log_ph.markdown("""
    <div class="agent-log">
        <div class="log-line active">▶ Step 1: Planning research queries...</div>
        <div class="log-line">○ Step 2: Web search pending</div>
        <div class="log-line">○ Step 3: Page scraping pending</div>
        <div class="log-line">○ Step 4: AI synthesis pending</div>
    </div>""", unsafe_allow_html=True)

    start_time = time.time()

    try:
        with st.spinner(""):
            state = run_research(topic.strip())
        elapsed = time.time() - start_time

        # ── Workflow done ──
        workflow_ph.markdown(render_workflow(5), unsafe_allow_html=True)

        # ── Agent log ──
        log_html = '<div class="agent-log">'
        for msg in state.get("status_log", []):
            cls = "error" if "❌" in msg else "done"
            log_html += f'<div class="log-line {cls}">{msg}</div>'
        log_ph.markdown(log_html + '</div>', unsafe_allow_html=True)

        # ── Metrics ──
        n_queries = len(state.get("queries", []))
        n_sources = len(state.get("sources", []))
        n_scraped = sum(1 for s in state.get("sources", []) if s.get("scraped"))
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-number">{n_queries}</span>
                <span class="metric-label">Queries Run</span>
            </div>
            <div class="metric-card">
                <span class="metric-number">{n_sources}</span>
                <span class="metric-label">Sources Found</span>
            </div>
            <div class="metric-card">
                <span class="metric-number">{n_scraped}</span>
                <span class="metric-label">Pages Scraped</span>
            </div>
            <div class="metric-card">
                <span class="metric-number">{elapsed:.1f}s</span>
                <span class="metric-label">Time Taken</span>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Query tags ──
        if state.get("queries"):
            tags = "".join(f'<span class="query-tag">🔍 {q}</span>' for q in state["queries"])
            st.markdown(f'<div style="margin:0.5rem 0 1.5rem">{tags}</div>', unsafe_allow_html=True)

        # ── Parse answer into summary + insights ──
        answer = state.get("answer", "No answer generated.")
        summary_lines = []
        insight_lines = []
        in_insights = False

        for line in answer.split("\n"):
            line = line.strip()
            if not line:
                continue
            if "key takeaway" in line.lower() or "key insight" in line.lower():
                in_insights = True
                continue
            if in_insights and line.startswith(("•", "-", "*")):
                clean = re.sub(r"^[•\-\*]+\s*", "", line)
                insight_lines.append(clean)
            else:
                summary_lines.append(line)

        # ── Research Summary ──
        summary_html = bold_to_html(" ".join(summary_lines[:8]))
        st.markdown(f"""
        <div class="results-section">
            <div class="section-title">📋 Research Summary</div>
            <div class="summary-text">{summary_html}</div>
        </div>""", unsafe_allow_html=True)

        # ── Key Insights ──
        if insight_lines:
            items_html = ""
            for insight in insight_lines[:6]:
                items_html += f'<div class="insight-item"><div class="insight-bullet"></div><div>{bold_to_html(insight)}</div></div>'
            st.markdown(f"""
            <div class="results-section">
                <div class="section-title">💡 Key Insights</div>
                {items_html}
            </div>""", unsafe_allow_html=True)

        # ── Sources ──
        sources = state.get("sources", [])
        if sources:
            src_html = ""
            for i, src in enumerate(sources, 1):
                title   = src.get("title", "Untitled") or "Untitled"
                url     = src.get("url", "#")
                snippet = src.get("snippet", "")[:180]
                domain  = url.split("/")[2] if url.startswith("http") and len(url.split("/")) > 2 else url
                badge   = '<span class="source-badge-full">● Full Text</span>' if src.get("scraped") else '<span class="source-badge-snip">● Snippet</span>'
                src_html += f"""
                <div class="source-card">
                    <div class="source-header">
                        <span class="source-num">SOURCE {i:02d}</span>
                        {badge}
                    </div>
                    <div class="source-title">{title}</div>
                    <div class="source-url">{domain}</div>
                    <div class="source-snippet">{snippet}...</div>
                    <a href="{url}" target="_blank" class="read-link">Read Article →</a>
                </div>"""
            st.markdown(f"""
            <div class="results-section">
                <div class="section-title">🔗 Sources ({len(sources)})</div>
                {src_html}
            </div>""", unsafe_allow_html=True)

        # ── Download ──
        full_report = f"# Research Report: {topic}\n\n## Summary\n{answer}\n\n## Sources\n"
        for i, src in enumerate(sources, 1):
            full_report += f"{i}. [{src.get('title', 'Untitled')}]({src.get('url', '')})\n"

        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            st.download_button(
                label="⬇️ Download Markdown",
                data=full_report,
                file_name=f"research_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_b:
            st.download_button(
                label="⬇️ Download Text",
                data=full_report,
                file_name=f"research_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    except Exception as e:
        workflow_ph.empty()
        log_ph.empty()
        st.markdown(f'<div class="warn-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        logging.exception("Pipeline error")

elif research_clicked and not topic.strip():
    st.warning("Please enter a research question.")

else:
    st.markdown(render_workflow(0), unsafe_allow_html=True)

