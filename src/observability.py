"""Internal observability context; no application behavior is changed."""
from __future__ import annotations

from contextvars import ContextVar

_REQUEST_ID: ContextVar[str | None] = ContextVar("observability_request_id", default=None)


def set_request_id(request_id: str | None):
    return _REQUEST_ID.set(request_id)


def reset_request_id(token) -> None:
    _REQUEST_ID.reset(token)


def get_request_id() -> str:
    return _REQUEST_ID.get() or "none"
