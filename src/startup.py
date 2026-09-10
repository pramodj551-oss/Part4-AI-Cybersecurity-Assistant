"""Startup dependency validation and recovery-safe runtime checks."""

from __future__ import annotations

import importlib
import logging

logger = logging.getLogger(__name__)

# Keep this list limited to application modules whose import is required for
# the RAG runtime. Optional tooling must not make the service unready.
_REQUIRED_RUNTIME_MODULES = (
    "src.llm",
    "src.prompt_builder",
    "src.retriever",
    "src.vector_store",
)


def check_runtime_dependencies() -> bool:
    """Return False instead of crashing when a required module is unavailable."""
    for module_name in _REQUIRED_RUNTIME_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception:
            logger.exception("Required runtime dependency unavailable: %s", module_name)
            return False
    return True


def check_startup() -> bool:
    """Validate required runtime imports for startup/readiness checks."""
    return check_runtime_dependencies()
