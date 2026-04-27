import os
import mysql.connector
from dotenv import load_dotenv

# Load credentials from the shared database/.env file
_env_path = os.path.join(os.path.dirname(__file__), '..', 'database', '.env')
load_dotenv(_env_path)

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "personal_finance"),
}


def get_db_connection():
    """Return a new MySQL connection using shared config."""
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


# ── LLM Configuration ─────────────────────────────────────────────────────────

def get_llm_config() -> dict:
    """
    Returns LLM provider settings read from the shared .env file.

    Required .env keys:
      LLM_PROVIDER  = groq | gemini | ollama   (default: groq)
      LLM_API_KEY   = your API key             (not needed for ollama)
      LLM_MODEL     = model name               (optional, sensible defaults applied)
      OLLAMA_URL    = http://localhost:11434    (only for ollama provider)
    """
    return {
        "provider":   os.getenv("LLM_PROVIDER", "groq"),
        "api_key":    os.getenv("LLM_API_KEY", ""),
        "model":      os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
    }
