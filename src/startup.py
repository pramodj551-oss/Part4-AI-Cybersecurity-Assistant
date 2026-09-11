"""Startup dependency validation and recovery-safe runtime checks."""

from __future__ import annotations

import importlib
import logging
import os

logger = logging.getLogger(__name__)

# Keep this list limited to application modules whose import is required for
# the RAG runtime. Optional tooling must not make the service unready.
_REQUIRED_RUNTIME_MODULES = (
    "src.llm",
    "src.prompt_builder",
    "src.retriever",
    "src.vector_store",
)

_vector_store_initialized = False


def check_runtime_dependencies() -> bool:
    """Return False instead of crashing when a required module is unavailable."""
    for module_name in _REQUIRED_RUNTIME_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception:
            logger.exception("Required runtime dependency unavailable: %s", module_name)
            return False
    return True


def initialize_vector_store() -> bool:
    """Load the verified production FAISS artifact into the application process."""
    global _vector_store_initialized

    if _vector_store_initialized:
        return True

    try:
        from src.vector_store import vector_store_manager

        vector_store_manager.load()
        _vector_store_initialized = True
        logger.info("Verified FAISS vector store initialized successfully.")
        return True
    except Exception:
        logger.exception("Verified FAISS vector store initialization failed.")
        return False


def check_startup() -> bool:
    """Validate dependencies and require FAISS initialization in production."""
    if not check_runtime_dependencies():
        return False

    environment = os.getenv("APP_ENVIRONMENT", "development").strip().lower()
    if environment not in {"production", "prod"}:
        return True

    return initialize_vector_store()
