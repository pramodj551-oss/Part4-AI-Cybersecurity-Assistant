"""Application configuration for the cybersecurity RAG assistant."""

from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
PROMPTS_DIR = BASE_DIR / "prompts"
LOG_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# The repository's tracked dataset is the authoritative incident source.
INCIDENT_DATASET = DATA_DIR / "cybersecurity_incident_reports.csv"
FAQ_DATASET = DATA_DIR / "faq.csv"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
SOP_DOCUMENTS_DIR = DATA_DIR / "sop_documents"

VECTOR_INDEX_PATH = VECTORSTORE_DIR / "faiss_index"

APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "development").strip().lower()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# Local Ollama remains the development default. Production may use the
# OpenAI-compatible Groq endpoint when LLM_PROVIDER=groq.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", "llama2")).strip()
API_KEY = os.getenv("API_KEY", os.getenv("GROQ_API_KEY", "ollama")).strip()
_default_api_base = (
    "https://api.groq.com/openai/v1"
    if LLM_PROVIDER == "groq"
    else "http://localhost:11434/v1"
)
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    os.getenv("OLLAMA_API_BASE", _default_api_base),
).rstrip("/")

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5
SEARCH_TYPE = "similarity"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = LOG_DIR / "rag_assistant.log"

APP_TITLE = "AI-Powered Cybersecurity Incident Assistant"
APP_ICON = "🛡️"
PAGE_LAYOUT = "wide"


def validate_production_config() -> None:
    """Fail closed when production configuration is missing or insecure."""
    if APP_ENVIRONMENT not in {"production", "prod"}:
        return

    required = {
        "AUTH_USERNAME": os.getenv("AUTH_USERNAME", "").strip(),
        "AUTH_PASSWORD_HASH": os.getenv("AUTH_PASSWORD_HASH", "").strip(),
        "API_KEY": API_KEY,
        "LLM_PROVIDER": LLM_PROVIDER,
        "LLM_MODEL": LLM_MODEL,
        "API_BASE_URL": API_BASE_URL,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Production configuration is incomplete: " + ", ".join(sorted(missing))
        )

    insecure_defaults = []
    if API_KEY.lower() in {"ollama", "changeme", "change-me", "test", "dummy", "placeholder"}:
        insecure_defaults.append("API_KEY")
    if LLM_MODEL.lower() == "llama2":
        insecure_defaults.append("LLM_MODEL")
    if API_BASE_URL.lower().startswith(("http://localhost", "http://127.0.0.1", "http://0.0.0.0")):
        insecure_defaults.append("API_BASE_URL")
    if not os.getenv("AUTH_PASSWORD_HASH", "").strip().startswith("pbkdf2_sha256$"):
        insecure_defaults.append("AUTH_PASSWORD_HASH")

    if insecure_defaults:
        raise RuntimeError(
            "Production configuration uses insecure/default values: "
            + ", ".join(sorted(set(insecure_defaults)))
        )


for directory in (MODEL_DIR, VECTORSTORE_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

validate_production_config()
