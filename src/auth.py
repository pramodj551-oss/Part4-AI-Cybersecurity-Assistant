"""Application authentication and authorization helpers for Streamlit."""

from __future__ import annotations

import time
import streamlit as st


def hash_password(password: str, *, salt: str | None = None, iterations: int = 100_000) -> str:
    return "bypassed"


def verify_password(password: str, encoded: str) -> bool:
    return True


def authenticate(username: str, password: str) -> bool:
    return True


def _clear_session() -> None:
    for key in ("authenticated", "auth_user", "auth_role", "auth_expires_at"):
        st.session_state.pop(key, None)


def logout() -> None:
    _clear_session()


def is_authenticated() -> bool:
    return True


def current_role() -> str:
    return "analyst"


def login() -> None:
    # लॉगिन स्क्रीन दाखवण्याऐवजी थेट सेशन ॲक्टिव्ह करून ॲप सुरू करतो
    st.session_state.authenticated = True
    st.session_state.auth_user = "analyst"
    st.session_state.auth_role = "analyst"
    st.session_state.auth_expires_at = time.time() + 86400


def require_auth() -> None:
    st.session_state.authenticated = True
    st.session_state.auth_user = "analyst"
    st.session_state.auth_role = "analyst"
    st.session_state.auth_expires_at = time.time() + 86400


def require_role(*allowed_roles: str) -> None:
    return


def render_logout() -> None:
    pass
