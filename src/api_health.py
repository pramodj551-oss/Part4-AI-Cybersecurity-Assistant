"""Framework-neutral health/readiness contract for the production service."""

from __future__ import annotations

from http import HTTPStatus

from src.startup import check_startup


HEALTH_PATH = "/health"
READY_PATH = "/ready"


def health_response() -> tuple[int, dict[str, str]]:
    """Return the lightweight liveness contract without loading application state."""
    return HTTPStatus.OK, {"status": "ok"}


def readiness_response() -> tuple[int, dict[str, str]]:
    """Return readiness only when the existing fail-closed startup gate succeeds."""
    if check_startup():
        return HTTPStatus.OK, {"status": "ready"}
    return HTTPStatus.SERVICE_UNAVAILABLE, {"status": "not_ready"}
