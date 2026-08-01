"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Configuration Module
Version: 4.0
==========================================================
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# ----------------------------------------------------------
# Load Environment Variables
# ----------------------------------------------------------

load_dotenv()

# ----------------------------------------------------------
# Project Directories
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
PROMPTS_DIR = BASE_DIR / "prompts"
LOG_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# ----------------------------------------------------------
# Data Files
# ----------------------------------------------------------

INCIDENT_DATASET = DATA_DIR / "cybersecurity_incidents.csv"
FAQ_DATASET = DATA_DIR / "faq.csv"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
SOP_DOCUMENTS_DIR = DATA_DIR / "sop_documents"

# ----------------------------------------------------------
# Vector Store
# ----------------------------------------------------------

VECTOR_INDEX_PATH = VECTORSTORE_DIR / "faiss_index"

# ----------------------------------------------------------
# Embedding Configuration
# ----------------------------------------------------------

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# ----------------------------------------------------------
# LLM Configuration
# ----------------------------------------------------------

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "openai"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gpt-4.1-mini"
)

API_KEY = os.getenv("API_KEY", "")

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    ""
)

TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.2")
)

MAX_TOKENS = int(
    os.getenv("MAX_TOKENS", "1024")
)

# ----------------------------------------------------------
# Text Splitting
# ----------------------------------------------------------

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

# ----------------------------------------------------------
# Retrieval
# ----------------------------------------------------------

TOP_K = 5

SEARCH_TYPE = "similarity"

# ----------------------------------------------------------
# Logging
# ----------------------------------------------------------

LOG_LEVEL = "INFO"

LOG_FILE = LOG_DIR / "rag_assistant.log"

# ----------------------------------------------------------
# Streamlit
# ----------------------------------------------------------

APP_TITLE = "AI-Powered Cybersecurity Incident Assistant"

APP_ICON = "🛡️"

PAGE_LAYOUT = "wide"

# ----------------------------------------------------------
# Create Required Directories
# ----------------------------------------------------------

for directory in (
    MODEL_DIR,
    VECTORSTORE_DIR,
    LOG_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True
    )
