"""Startup dependency validation and recovery-safe runtime checks."""

from __future__ import annotations

import importlib
import logging
import os
import re

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


def _sanitize_exception(error: Exception) -> str:
    """Return a diagnostic-safe exception message without obvious secrets."""
    message = str(error)
    message = re.sub(
        r"(?i)(api[_-]?key|password|token|secret)\s*[=:]\s*[^\s,;]+",
        r"\1=<redacted>",
        message,
    )
    return message[:500]


def _probe_log(message: str) -> None:
    """Emit startup probe evidence through both logger and stdout."""
    logger.info(message)
    print(f"STARTUP_PROBE: {message}", flush=True)


def check_runtime_dependencies() -> bool:
    """Return False instead of crashing when a required module is unavailable."""
    _probe_log("check_runtime_dependencies entered")

    for module_name in _REQUIRED_RUNTIME_MODULES:
        _probe_log(f"checking runtime dependency: {module_name}")
        try:
            importlib.import_module(module_name)
        except Exception as error:
            diagnostic = _sanitize_exception(error)
            logger.exception("Required runtime dependency unavailable: %s", module_name)
            print(
                "STARTUP_PROBE: runtime dependency FAILED: "
                f"{module_name}; exception={type(error).__name__}; message={diagnostic}",
                flush=True,
            )
            return False
        _probe_log(f"runtime dependency OK: {module_name}")

    _probe_log("all required runtime dependencies OK")
    return True


def initialize_vector_store() -> bool:
    """Load the verified production FAISS artifact into the application process."""
    global _vector_store_initialized

    if _vector_store_initialized:
        _probe_log("FAISS initialization already completed; reusing initialized store")
        return True

    _probe_log("production FAISS initialization starting")

    try:
        from src.vector_store import vector_store_manager

        _probe_log("calling vector_store_manager.load()")
        vector_store_manager.load()
        _vector_store_initialized = True
        logger.info("Verified FAISS vector store initialized successfully.")
        _probe_log("FAISS initialization succeeded")
        return True
    except Exception as error:
        diagnostic = _sanitize_exception(error)
        logger.exception("Verified FAISS vector store initialization failed.")
        print(
            "STARTUP_PROBE: FAISS initialization FAILED: "
            f"exception={type(error).__name__}; message={diagnostic}",
            flush=True,
        )
        return False


def check_startup() -> bool:
    """Validate dependencies and require FAISS initialization in production."""
    _probe_log("check_startup entered")

    if not check_runtime_dependencies():
        _probe_log("check_startup result=False; runtime dependency validation failed")
        return False

    environment = os.getenv("APP_ENVIRONMENT", "development").strip().lower()
    _probe_log(f"APP_ENVIRONMENT={environment}")

    if environment not in {"production", "prod"}:
        _probe_log("check_startup result=True; non-production environment")
        return True

    result = initialize_vector_store()
    _probe_log(f"check_startup result={result}")
    return result
