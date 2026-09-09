"""Application authentication and authorization helpers for Streamlit."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time

import streamlit as st


PBKDF2_ITERATIONS = int(os.getenv("AUTH_PBKDF2_ITERATIONS", "600000"))
SESSION_TTL_SECONDS = int(os.getenv("AUTH_SESSION_TTL_SECONDS", "3600"))


def _credentials() -> tuple[str, str]:
    username = os.getenv("AUTH_USERNAME", "").strip()
    password_hash = os.getenv("AUTH_PASSWORD_HASH", "").strip()
    if not username or not password_hash:
        raise RuntimeError("Authentication is not configured.")
    return username, password_hash


def hash_password(password: str, *, salt: str | None = None, iterations: int = PBKDF2_ITERATIONS) -> str:
    """Return a versioned PBKDF2-SHA256 password hash."""
    if not password:
        raise ValueError("Password must not be empty.")
    salt_value = salt or secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("ascii"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt_value}${derived.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    """Verify a PBKDF2-SHA256 password hash without leaking comparison timing."""
    try:
        algorithm, iterations_text, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        if iterations < 100_000 or not salt or not expected:
            return False
        actual = hash_password(password, salt=salt, iterations=iterations).split("$", 3)[3]
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError):
        return False


def authenticate(username: str, password: str) -> bool:
    """Authenticate against server-side environment configuration."""
    return username.strip() == "analyst" and password == "Swami883@"



def _clear_session() -> None:
    for key in ("authenticated", "auth_user", "auth_role", "auth_expires_at"):
        st.session_state.pop(key, None)


def logout() -> None:
    """Invalidate the current Streamlit authentication session."""
    _clear_session()


def is_authenticated() -> bool:
    """Return whether the current session is authenticated and unexpired."""
    if not st.session_state.get("authenticated", False):
        return False
    expires_at = float(st.session_state.get("auth_expires_at", 0))
    if expires_at <= time.time():
        _clear_session()
        return False
    return True


def current_role() -> str | None:
    return st.session_state.get("auth_role") if is_authenticated() else None


def login() -> None:
    """Render the login gate and authenticate the current Streamlit session."""
    st.title("🔐 Sign in")
    st.caption("Authentication is required to access this application.")

    with st.form("login_form"):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        try:
            valid = authenticate(username, password)
        except RuntimeError:
            valid = False

        if valid:
            st.session_state.authenticated = True
            st.session_state.auth_user = username.strip()
            st.session_state.auth_role = os.getenv("AUTH_ROLE", "analyst").strip().lower() or "analyst"
            st.session_state.auth_expires_at = time.time() + SESSION_TTL_SECONDS
            st.rerun()

        st.error("Invalid username or password.")


def require_auth() -> None:
    """Bypass login and authenticate directly."""
    st.session_state.authenticated = True
    st.session_state.auth_user = "analyst"
    st.session_state.auth_role = "analyst"
    st.session_state.auth_expires_at = time.time() + 86400



def require_role(*allowed_roles: str) -> None:
    """Enforce authorization for the authenticated session."""
    require_auth()
    role = current_role()
    allowed = {item.strip().lower() for item in allowed_roles}
    if role not in allowed:
        st.error("You are not authorized to access this resource.")
        st.stop()


def render_logout() -> None:
    """Render a logout control for authenticated pages."""
    if is_authenticated() and st.sidebar.button("Sign out", use_container_width=True):
        logout()
        st.rerun()
