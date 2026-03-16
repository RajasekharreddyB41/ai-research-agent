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
from database import save_research, get_history, get_research_by_id, delete_research  # noqa: E402

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
.log-line        { color: #64748b; }
.log-line.active { color: #38bdf8; }
.log-line.done   { color: #4ade80; }
.log-line.error  { color: #f87171; }

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

div[data-testid="stVerticalBlock"]:has(> * > .md-card) {
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 0.5rem 1.5rem 1.5rem;
    margin: 1.5rem 0;
}
div[data-testid="stVerticalBlock"]:has(> * > .md-card) p {
    color: #334155; font-size: 0.95rem; line-height: 1.8; margin-bottom: 0.6rem;
}
div[data-testid="stVerticalBlock"]:has(> * > .md-card) ul,
div[data-testid="stVerticalBlock"]:has(> * > .md-card) ol {
    color: #334155; font-size: 0.95rem; line-height: 1.8; padding-left: 1.4rem; margin-bottom: 0.6rem;
}
div[data-testid="stVerticalBlock"]:has(> * > .md-card) li { margin-bottom: 0.35rem; }
div[data-testid="stVerticalBlock"]:has(> * > .md-card) h1,
div[data-testid="stVerticalBlock"]:has(> * > .md-card) h2,
div[data-testid="stVerticalBlock"]:has(> * > .md-card) h3,
div[data-testid="stVerticalBlock"]:has(> * > .md-card) h4 {
    color: #0f172a; font-weight: 700; margin-top: 1.2rem; margin-bottom: 0.4rem;
}
div[data-testid="stVerticalBlock"]:has(> * > .md-card) strong { color: #1e40af; }

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

    st.markdown("### 🔑 API Keys")
    groq_key_input = st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_api_key", ""),
        type="password",
        placeholder="gsk_...",
        key="groq_key_widget",
    )
    tavily_key_input = st.text_input(
        "Tavily API Key",
        value=st.session_state.get("tavily_api_key", ""),
        type="password",
        placeholder="tvly-...",
        key="tavily_key_widget",
    )
    if groq_key_input:
        st.session_state["groq_api_key"] = groq_key_input
        settings.GROQ_API_KEY = groq_key_input
    if tavily_key_input:
        st.session_state["tavily_api_key"] = tavily_key_input
        settings.TAVILY_API_KEY = tavily_key_input

    with st.expander("How to get API keys?"):
        st.markdown(
            "**Groq** — [console.groq.com](https://console.groq.com)\n\n"
            "**Tavily** — [app.tavily.com](https://app.tavily.com)"
        )

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
    st.markdown("---")

    st.markdown("### 📜 Research History")
    history = get_history(limit=15)
    if history:
        active_id = st.session_state.get("active_record", {}).get("id")
        for record in history:
            label = record["topic"][:28] + "…" if len(record["topic"]) > 30 else record["topic"]
            col_h, col_d = st.sidebar.columns([4, 1])
            with col_h:
                is_active = record["id"] == active_id
                btn_label = f"{'▶ ' if is_active else ''}{label}"
                if st.button(btn_label, key=f"h_{record['id']}", use_container_width=True):
                    st.session_state["load_history_id"] = record["id"]
                    st.rerun()
            with col_d:
                if st.button("🗑", key=f"d_{record['id']}"):
                    delete_research(record["id"])
                    if record["id"] == active_id:
                        st.session_state.pop("active_record", None)
                        st.session_state.pop("last_answer", None)
                    st.rerun()
            st.sidebar.caption(f"{record['created_at']} · {record['num_sources']} sources")
    else:
        st.sidebar.caption("No research history yet.")


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
        f'<div class="warn-box">⚠️ Missing: <strong>{", ".join(missing)}</strong> — '
        f'enter them in the sidebar or set in your .env file.</div>',
        unsafe_allow_html=True,
    )


# ── Search input ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="search-container"><div class="search-label">Research Question</div>',
    unsafe_allow_html=True,
)
topic = st.text_area(
    label="topic",
    placeholder="Research the impact of AI chips on data center infrastructure in 2026...",
    height=90,
    label_visibility="collapsed",
)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔍  Start Research", use_container_width=True):
        st.session_state["research_triggered"] = True
st.markdown("</div>", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────

def sanitize_llm_output(text: str) -> str:
    """Clean LLM output for safe Streamlit rendering."""
    text = text.replace("$", "")
    text = text.replace("\u2217", "*")
    text = text.replace("\u2022", "•")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = re.sub(r"\*\s\*([^*]+)\*\s\*", r"**\1**", text)
    text = re.sub(r"\*\s+\*", "**", text)
    text = re.sub(r"\*{3,}", "**", text)
    return text


def bold_to_html(text: str) -> str:
    """Convert **bold** markdown to <strong> HTML."""
    return re.sub(r"[*][*](.+?)[*][*]", r"<strong>\1</strong>", text)


def render_workflow(step: int) -> str:
    """Render agent workflow steps. step: 0=idle, 1-4=active node, 5=done."""
    steps = [
        ("🧠", "Query Planner"),
        ("🔍", "Web Search"),
        ("📄", "Page Scraper"),
        ("✨", "AI Synthesis"),
    ]
    html = (
        '<div class="workflow-container">'
        '<div class="workflow-title">Agent Workflow</div>'
        '<div class="workflow-steps">'
    )
    for i, (icon, label) in enumerate(steps):
        node = i + 1
        if step == 0:
            cls = "step-pending"
        elif node < step:
            cls, icon = "step-done", "✅"
        elif node == step:
            cls = "step-active"
        else:
            cls = "step-pending"
        html += f'<div class="workflow-step {cls}">{icon} {label}</div>'
        if i < len(steps) - 1:
            html += '<div class="workflow-arrow">→</div>'
    return html + "</div></div>"


def parse_insights(answer: str) -> tuple[list[str], list[str]]:
    """Split answer into (summary_lines, insight_lines)."""
    summary_lines: list[str] = []
    insight_lines: list[str] = []
    in_insights = False
    in_conclusion = False

    for line in answer.split("\n"):
        line = line.strip()
        if not line:
            continue
        if re.search(r"key (takeaway|insight|finding)", line, re.IGNORECASE):
            in_insights = True
            in_conclusion = False
            continue
        if re.match(r"^#{0,4}\s*conclusion\s*$", line, re.IGNORECASE):
            in_conclusion = True
            in_insights = False
            continue
        if in_insights and line.startswith(("•", "-", "*")):
            insight_lines.append(re.sub(r"^[•\-*]+\s*", "", line))
        elif in_insights and re.match(r"^\d+[.)]\s", line):
            insight_lines.append(re.sub(r"^\d+[.)]\s*", "", line))
        elif in_insights:
            insight_lines.append(line)
        elif in_conclusion:
            continue
        else:
            summary_lines.append(line)

    return summary_lines, insight_lines


def clean_text(text: str) -> str:
    """Strip HTML tags, entities and markdown for plain display."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&[a-zA-Z]{2,6};", " ", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*]{1,3}(.+?)[*]{1,3}", r"\1", text)
    text = re.sub(r"^\s*[*\-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def build_source_html(sources: list) -> str:
    """Build HTML for source cards — all text cleaned of HTML/markdown."""
    src_html = ""
    for i, src in enumerate(sources, 1):
        title = clean_text(src.get("title", "Untitled") or "Untitled")
        url = src.get("url", "#")
        snippet = clean_text(src.get("snippet", ""))[:180]
        domain = url.split("/")[2] if url.startswith("http") and len(url.split("/")) > 2 else url
        badge = (
            '<span class="source-badge-full">● Full Text</span>'
            if src.get("scraped")
            else '<span class="source-badge-snip">● Snippet</span>'
        )
        src_html += (
            '<div class="source-card">'
            '<div class="source-header">'
            f'<span class="source-num">SOURCE {i:02d}</span>{badge}'
            "</div>"
            f'<div class="source-title">{title}</div>'
            f'<div class="source-url">{domain}</div>'
            f'<div class="source-snippet">{snippet}...</div>'
            f'<a href="{url}" target="_blank" class="read-link">Read Article →</a>'
            "</div>"
        )
    return src_html


def render_key_insights(insight_lines: list[str]) -> None:
    """Render Key Insights card."""
    if not insight_lines:
        return
    items_html = ""
    for insight in insight_lines[:6]:
        items_html += (
            '<div class="insight-item">'
            '<div class="insight-bullet"></div>'
            f"<div>{bold_to_html(sanitize_llm_output(insight))}</div>"
            "</div>"
        )
    st.markdown(
        f'<div class="results-section">'
        f'<div class="section-title">💡 Key Insights</div>'
        f"{items_html}</div>",
        unsafe_allow_html=True,
    )


def _pdf_text(text: str) -> str:
    """Prepare text for PDF rendering."""
    text = text.replace("\\$", "$")
    text = re.sub(r"[*]{1,3}(.+?)[*]{1,3}", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"[^\x00-\xFF]", "", text)
    text = re.sub(r"[\x80-\x9f]", " ", text)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf(topic: str, answer: str, sources: list, date_str: str) -> bytes:
    """Generate a PDF research report."""
    from fpdf import FPDF

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    W = 180.0
    LEFT = 15.0
    RIGHT = 195.0

    def mc(text: str, h: float = 6.0) -> None:
        pdf.set_x(LEFT)
        pdf.multi_cell(W, h, _pdf_text(text), new_x="LMARGIN", new_y="NEXT")

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 23, 42)
    mc(topic, 9)
    pdf.set_x(LEFT)
    pdf.ln(1)

    # Date
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(LEFT)
    pdf.cell(W, 6, _pdf_text(f"Research Date: {date_str}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(LEFT)
    pdf.ln(3)

    # Divider
    pdf.set_draw_color(226, 232, 240)
    pdf.set_x(LEFT)
    pdf.line(LEFT, pdf.get_y(), RIGHT, pdf.get_y())
    pdf.set_x(LEFT)
    pdf.ln(6)

    # Section heading
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.set_x(LEFT)
    pdf.cell(W, 7, "Research Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(LEFT)
    pdf.ln(2)

    # Body
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)

    for line in answer.split("\n"):
        stripped = line.strip()
        if not stripped:
            pdf.set_x(LEFT)
            pdf.ln(3)
            continue

        if stripped.startswith("####"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(15, 23, 42)
            mc(re.sub(r"^#{4}\s*", "", stripped), 6)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(51, 65, 85)
        elif stripped.startswith("###"):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(15, 23, 42)
            mc(re.sub(r"^#{3}\s*", "", stripped), 7)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(51, 65, 85)
        elif stripped.startswith("##"):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            mc(re.sub(r"^#{2}\s*", "", stripped), 7)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(51, 65, 85)
        elif stripped.startswith("#"):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(15, 23, 42)
            mc(re.sub(r"^#\s*", "", stripped), 8)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(51, 65, 85)
        elif re.match(r"^[-*\u2022]\s+", stripped):
            bullet_text = re.sub(r'^[-*•]\s+', '', stripped)
            mc(f'  - {bullet_text}', 6)
        else:
            mc(stripped, 6)

        pdf.set_x(LEFT)
        pdf.ln(1)

    # Sources
    if sources:
        pdf.set_x(LEFT)
        pdf.ln(3)
        pdf.set_draw_color(226, 232, 240)
        pdf.line(LEFT, pdf.get_y(), RIGHT, pdf.get_y())
        pdf.set_x(LEFT)
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.set_x(LEFT)
        pdf.cell(W, 7, f"Sources ({len(sources)})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(LEFT)
        pdf.ln(2)

        for i, src in enumerate(sources, 1):
            title = src.get("title", "Untitled") or "Untitled"
            url = src.get("url", "") or ""
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(30, 64, 175)
            mc(f"{i}. {title}", 6)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 116, 139)
            mc(url[:120], 5)
            pdf.set_x(LEFT)
            pdf.ln(3)

    return bytes(pdf.output())


def render_downloads(topic_text: str, answer_raw: str, sources: list, date_str: str) -> None:
    """Render Markdown / Text / PDF download buttons."""
    full_report = f"# Research Report: {topic_text}\n\n## Summary\n{answer_raw}\n\n## Sources\n"
    for i, src in enumerate(sources, 1):
        full_report += f"{i}. [{src.get('title', 'Untitled')}]({src.get('url', '')})\n"

    pdf_bytes = generate_pdf(topic_text, answer_raw, sources, date_str)
    ts = int(time.time())

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.download_button(
            "⬇️ Download Markdown", data=full_report,
            file_name=f"research_{ts}.md", mime="text/markdown",
            use_container_width=True,
        )
    with col_b:
        st.download_button(
            "⬇️ Download Text", data=full_report,
            file_name=f"research_{ts}.txt", mime="text/plain",
            use_container_width=True,
        )
    with col_c:
        st.download_button(
            "⬇️ Download PDF", data=pdf_bytes,
            file_name=f"research_{ts}.pdf", mime="application/pdf",
            use_container_width=True,
        )


def render_metrics(
    n_queries: int,
    n_sources: int,
    n_scraped: int,
    elapsed: float | None = None,
) -> None:
    """Render the 4-column metrics grid."""
    if elapsed is not None:
        time_cell = (
            f'<span class="metric-number">{elapsed:.1f}s</span>'
            f'<span class="metric-label">Time Taken</span>'
        )
    else:
        time_cell = (
            '<span class="metric-number">—</span>'
            '<span class="metric-label">Cached Result</span>'
        )
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
        <div class="metric-card">{time_cell}</div>
    </div>""", unsafe_allow_html=True)


def render_sources_section(sources: list) -> None:
    """Render the Sources card."""
    if not sources:
        return
    st.markdown(
        f'<div class="results-section">'
        f'<div class="section-title">🔗 Sources ({len(sources)})</div>'
        f"{build_source_html(sources)}</div>",
        unsafe_allow_html=True,
    )


def render_query_tags(queries: list) -> None:
    """Render coloured query pills."""
    if not queries:
        return
    cleaned = [re.sub(r"^[•\-*\s]+", "", q).strip() for q in queries]
    tags = "".join(f'<span class="query-tag">🔍 {q}</span>' for q in cleaned if q)
    st.markdown(f'<div style="margin:0.5rem 0 1.5rem">{tags}</div>', unsafe_allow_html=True)


# ── Hydrate history record ────────────────────────────────────────────────────
_load_id = st.session_state.pop("load_history_id", None)
if _load_id:
    _rec = get_research_by_id(_load_id)
    if _rec:
        st.session_state["active_record"] = _rec
        st.session_state["last_answer"] = _rec["answer"]
        st.session_state["last_topic"] = _rec["topic"]
        st.session_state["last_sources"] = _rec["sources"]
        st.session_state["followup_history"] = []


# ── Research execution ────────────────────────────────────────────────────────
research_triggered = st.session_state.pop("research_triggered", False)

if research_triggered and topic.strip():
    st.session_state.pop("active_record", None)

    if missing:
        st.error(f"Missing API keys: {', '.join(missing)}. Enter them in the sidebar.")
        st.stop()

    from agent.research_agent import run_research  # noqa: E402

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

        workflow_ph.markdown(render_workflow(5), unsafe_allow_html=True)

        log_html = '<div class="agent-log">'
        for msg in state.get("status_log", []):
            cls = "error" if "❌" in msg else "done"
            log_html += f'<div class="log-line {cls}">{msg}</div>'
        log_html += '<div class="log-line done">✅ Research complete</div>'
        log_ph.markdown(log_html + "</div>", unsafe_allow_html=True)

        answer_raw = re.sub(r"<[^>]+>", "", state.get("answer", "No answer generated."))
        sources = state.get("sources", [])
        queries = state.get("queries", [])

        n_queries = len(queries)
        n_sources = len(sources)
        n_scraped = sum(1 for s in sources if s.get("scraped"))

        save_research(
            topic=topic.strip(),
            answer=answer_raw,
            sources=sources,
            queries=queries,
        )

        st.session_state["last_answer"] = answer_raw
        st.session_state["last_topic"] = topic.strip()
        st.session_state["last_sources"] = sources
        st.session_state["followup_history"] = []

        render_query_tags(queries)

        with st.container():
            st.markdown(
                '<div class="md-card"><div class="section-title">📋 Research Summary</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(sanitize_llm_output(answer_raw))

        _, insight_lines = parse_insights(answer_raw)
        render_key_insights(insight_lines)
        render_metrics(n_queries, n_sources, n_scraped, elapsed)
        render_sources_section(sources)
        render_downloads(topic.strip(), answer_raw, sources, time.strftime("%B %d, %Y"))

    except Exception as e:
        workflow_ph.empty()
        log_ph.empty()
        st.markdown(f'<div class="warn-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        logging.exception("Pipeline error")

elif research_triggered and not topic.strip():
    st.warning("Please enter a research question.")

elif st.session_state.get("active_record"):
    record = st.session_state["active_record"]
    answer_raw = record["answer"]
    sources = record["sources"]
    queries = record.get("queries", [])
    date_str = record.get("created_at", "")

    st.markdown(render_workflow(5), unsafe_allow_html=True)
    st.markdown(
        f'<div class="agent-log">'
        f'<div class="log-line done">📂 Loaded from history — {date_str}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    n_scraped = sum(1 for s in sources if s.get("scraped"))
    render_metrics(len(queries), len(sources), n_scraped)
    render_query_tags(queries)

    summary_lines, insight_lines = parse_insights(answer_raw)
    filtered_summary = "\n\n".join(summary_lines)
    with st.container():
        st.markdown(
            '<div class="md-card"><div class="section-title">📋 Research Summary</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(sanitize_llm_output(filtered_summary))

    render_key_insights(insight_lines)
    render_sources_section(sources)
    render_downloads(record["topic"], answer_raw, sources, date_str)

else:
    st.markdown(render_workflow(0), unsafe_allow_html=True)


# ── Follow-up questions ───────────────────────────────────────────────────────
if st.session_state.get("last_answer"):
    from langchain_groq import ChatGroq  # noqa: E402
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402

    st.markdown(
        '<div class="results-section">'
        '<div class="section-title">💬 Ask a Follow-up Question</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    for turn in st.session_state.get("followup_history", []):
        st.markdown(f"**You:** {turn['question']}")
        with st.container():
            st.markdown(
                '<div class="md-card"><div class="section-title">🤖 Answer</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(sanitize_llm_output(turn["answer"]))

    followup_q = st.text_input(
        "Follow-up question",
        placeholder="What else would you like to know?",
        label_visibility="collapsed",
        key="followup_input",
    )
    if st.button("Ask Follow-up", key="followup_btn"):
        st.session_state["followup_triggered"] = True

    followup_triggered = st.session_state.pop("followup_triggered", False)

    if followup_triggered and followup_q.strip():
        sources_ctx = ""
        for i, src in enumerate(st.session_state.get("last_sources", []), 1):
            title = src.get("title", "Untitled") or "Untitled"
            url = src.get("url", "")
            sources_ctx += f"  [Source {i}] {title} — {url}\n"

        system_prompt = (
            "You are a research assistant. Answer follow-up questions using ONLY "
            "the facts in the research summary and sources. Be concise. "
            "Use **bold** for key terms."
        )

        messages = [SystemMessage(content=system_prompt)]
        context_msg = (
            f"Research topic: '{st.session_state['last_topic']}'\n\n"
            f"Summary:\n{st.session_state['last_answer']}\n\n"
            f"Sources:\n{sources_ctx}"
        )
        messages.append(HumanMessage(content=context_msg))
        messages.append(
            AIMessage(content="Understood. What would you like to know?")
        )

        for turn in st.session_state.get("followup_history", []):
            messages.append(HumanMessage(content=turn["question"]))
            messages.append(AIMessage(content=turn["answer"]))

        messages.append(HumanMessage(content=followup_q.strip()))

        try:
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=1024,
            )

            st.markdown(f"**You:** {followup_q.strip()}")
            with st.container():
                st.markdown(
                    '<div class="md-card"><div class="section-title">🤖 Answer</div></div>',
                    unsafe_allow_html=True,
                )
                followup_raw = st.write_stream(
                    chunk.content for chunk in llm.stream(messages) if chunk.content
                )

            st.session_state.setdefault("followup_history", []).append({
                "question": followup_q.strip(),
                "answer": followup_raw,
            })

        except Exception as e:
            st.markdown(
                f'<div class="warn-box">❌ Follow-up error: {e}</div>',
                unsafe_allow_html=True,
            )
