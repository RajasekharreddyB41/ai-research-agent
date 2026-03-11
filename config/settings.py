"""
Configuration settings for the AI Research Agent.
All secrets are loaded from environment variables — never hardcoded.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- LLM ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # --- Search (reduced for speed) ---
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "3"))
    MAX_SCRAPE_CHARS: int = int(os.getenv("MAX_SCRAPE_CHARS", "2000"))

    # --- Agent ---
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "6"))

    # --- Parallel scraping ---
    MAX_SCRAPE_WORKERS: int = int(os.getenv("MAX_SCRAPE_WORKERS", "5"))

    def validate(self) -> list[str]:
        missing = []
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        return missing


settings = Settings()
