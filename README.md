title: AI Research Agent
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
# 🔬 AI Research Agent

> Autonomous web research powered by LangGraph + Groq LLM + Azure App Service

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Azure-0078D4?style=for-the-badge&logo=microsoft-azure)](https://ai-research-agent-rb2026.azurewebsites.net)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

---

## 🚀 Live Demo

**[https://ai-research-agent-rb2026.azurewebsites.net](https://ai-research-agent-rb2026.azurewebsites.net)**

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
│  Query Planner  │  llama-3.1-8b-instant  →  Generates 3–5 targeted sub-queries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Web Search    │  Tavily Search API     →  Fetches top results per query
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Page Scraper   │  BeautifulSoup         →  Parallel scraping of up to 8 pages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Synthesis   │  llama-3.3-70b-versatile → Structured report with citations
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
| 🔄 **CI/CD Pipeline** | Auto-deploys to Azure on every GitHub push |
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
| **Infra** | Docker → Azure Container Registry → Azure App Service |
| **CI/CD** | GitHub Actions |

---

## 📁 Project Structure

```
ai-research-agent/
├── app.py                        # Streamlit UI — recruiter-level design
├── database.py                   # SQLite research history
├── requirements.txt
├── Dockerfile
├── startup.sh                    # Azure App Service entrypoint
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


---

## 🎯 Why This Project Matters

This project demonstrates:

- ✅ Agentic AI system design (LangGraph)
- ✅ Real-time data integration (Tavily)
- ✅ Scalable architecture (Docker + Azure)
- ✅ Production deployment with CI/CD
- ✅ Full-stack AI engineering (UI → backend → infra)

---

## 👨‍💻 Developed By

**Rajasekhar Reddy Byreddy**  
Passionate about building intelligent AI systems that make information accessible.

🔗 GitHub: https://github.com/RajasekharreddyB41

---

## 📄 License

MIT License — feel free to use this project as a reference.



