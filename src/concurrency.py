"""Application-level concurrency control for expensive RAG operations."""

from __future__ import annotations

import os
from threading import BoundedSemaphore

DEFAULT_MAX_IN_FLIGHT = 1
MAX_ALLOWED_IN_FLIGHT = 8


def get_max_in_flight() -> int:
    """Return a safe, bounded concurrency value from the environment."""
    raw_value = os.getenv("RAG_MAX_IN_FLIGHT", str(DEFAULT_MAX_IN_FLIGHT)).strip()
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_MAX_IN_FLIGHT

    if value < 1:
        return DEFAULT_MAX_IN_FLIGHT
    return min(value, MAX_ALLOWED_IN_FLIGHT)


class ConcurrencyLimitError(RuntimeError):
    """Raised when the expensive RAG execution slot is already occupied."""

    def __init__(self) -> None:
        super().__init__("The assistant is busy processing another request. Please try again shortly.")


class RAGConcurrencyGuard:
    """Non-blocking, bounded guard for the expensive RAG/LLM execution path."""

    def __init__(self, max_in_flight: int | None = None) -> None:
        self.max_in_flight = max_in_flight or get_max_in_flight()
        self._semaphore = BoundedSemaphore(self.max_in_flight)

    def acquire(self) -> None:
        if not self._semaphore.acquire(blocking=False):
            raise ConcurrencyLimitError()

    def release(self) -> None:
        self._semaphore.release()

    def __enter__(self) -> "RAGConcurrencyGuard":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()
