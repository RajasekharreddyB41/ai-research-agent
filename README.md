---
title: AI Research Agent
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
---

# 🔬 AI Research Agent

> Autonomous web research powered by LangGraph + Groq LLM + Hugging Face Spaces

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/Rajasekhar-06/ai-research-agent)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/RajasekharreddyB41/ai-research-agent)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

---

## 🚀 Live Demo

**[https://huggingface.co/spaces/Rajasekhar-06/ai-research-agent](https://huggingface.co/spaces/Rajasekhar-06/ai-research-agent)**

Enter your Groq and Tavily API keys in the sidebar to try it live.

---

## 📌 What It Does

Unlike traditional AI models that rely on static training data, this system:

- 🌐 Searches the **live internet in real-time**
- 📄 Scrapes multiple trusted sources simultaneously
- 🧠 Synthesizes results into a **clear, accurate report with citations**
- ❌ Reduces hallucinations by grounding responses in real data

**Example queries:**
- *"AI chip market leaders in 2026"*
- *"Future of electric vehicles and battery technology"*
- *"Impact of AI on healthcare diagnostics"*

---

## 🏗️ Agent Pipeline

```
User Query
    │
    ▼
┌─────────────────┐
│  Query Planner  │  llama-3.1-8b-instant    →  Generates 3–5 targeted sub-queries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Web Search    │  Tavily Search API        →  Fetches top results per query
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Page Scraper   │  BeautifulSoup            →  Parallel scraping of up to 8 pages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Synthesis   │  llama-3.3-70b-versatile  →  Structured report with citations
└─────────────────┘
         │
         ▼
  Research Report
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Autonomous Agents** | 4-node LangGraph pipeline — plan, search, scrape, synthesize |
| ⚡ **Fast Responses** | Parallel scraping + dual LLM strategy (8B for planning, 70B for synthesis) |
| 💬 **Follow-up Questions** | Ask follow-up questions on any research result |
| 📜 **Research History** | Every research saved to SQLite — reload any past result |
| ⬇️ **Export Reports** | Download as Markdown, Text, or PDF |
| 🔄 **CI/CD Pipeline** | Auto-deploys on every GitHub push via GitHub Actions |
| 🎨 **Recruiter-Ready UI** | Professional dark blue hero, workflow visualization, source cards |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq API — llama-3.3-70b-versatile + llama-3.1-8b-instant |
| **Orchestration** | LangGraph 0.2 |
| **Search** | Tavily Search API |
| **Scraping** | BeautifulSoup4 + concurrent.futures |
| **UI** | Streamlit 1.41 |
| **Storage** | SQLite (research history) |
| **Infra** | Docker → Hugging Face Spaces |
| **CI/CD** | GitHub Actions |

---

## 📁 Project Structure

```
ai-research-agent/
├── app.py                        # Streamlit UI — recruiter-level design
├── database.py                   # SQLite research history
├── requirements.txt
├── Dockerfile
├── agent/
│   ├── __init__.py
│   └── research_agent.py         # LangGraph 4-node pipeline
├── utils/
│   ├── __init__.py
│   ├── search.py                 # Tavily search wrapper
│   └── scraper.py                # Parallel BeautifulSoup scraper
├── config/
│   ├── __init__.py
│   └── settings.py               # Environment-based config
└── .github/
    └── workflows/
        └── deploy-appservice.yml # CI/CD: lint → build → push → deploy
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- Docker Desktop
- A [Groq API key](https://console.groq.com)
- A [Tavily API key](https://app.tavily.com)

### 1. Clone the repo
```bash
git clone https://github.com/RajasekharreddyB41/ai-research-agent.git
cd ai-research-agent
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
MAX_SEARCH_RESULTS=5
MAX_SCRAPE_CHARS=3000
```

### 5. Run locally
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker

```bash
# Build
docker build --platform linux/amd64 -t ai-research-agent .

# Run
docker run -p 7860:7860 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  ai-research-agent
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | required | Groq LLM API key |
| `TAVILY_API_KEY` | required | Tavily Search API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model for synthesis |
| `MAX_SEARCH_RESULTS` | `5` | Max sources per query |
| `MAX_SCRAPE_CHARS` | `3000` | Max chars scraped per page |
| `MAX_SCRAPE_WORKERS` | `5` | Parallel scraping threads |
| `REQUEST_TIMEOUT` | `6` | HTTP timeout in seconds |
| `DB_PATH` | `/tmp/research_history.db` | SQLite database path |

---

## 🎯 Why This Project Matters

This project demonstrates:

- ✅ Agentic AI system design (LangGraph)
- ✅ Real-time data integration (Tavily)
- ✅ Scalable architecture (Docker + Hugging Face)
- ✅ Production deployment with CI/CD
- ✅ Full-stack AI engineering (UI → backend → infra)

---

## 👨‍💻 Developed By

**Rajasekhar Reddy Byreddy**
Student @ New England College
Building a production-grade AI Engineer portfolio.

🔗 GitHub: [RajasekharreddyB41](https://github.com/RajasekharreddyB41)

---

## 📄 License

MIT License — feel free to use this project as a reference.
