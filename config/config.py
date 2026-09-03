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

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# Default to the documented local Ollama deployment. Remote providers remain
# possible through the OpenAI-compatible API endpoint environment variables.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", "llama2"))
API_KEY = os.getenv("API_KEY", "ollama")
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1"),
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

for directory in (MODEL_DIR, VECTORSTORE_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)
