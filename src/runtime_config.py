"""Unified deployment configuration lookup for Render and Streamlit Secrets."""

from __future__ import annotations

import os
from collections.abc import Mapping


def get_setting(name: str, default: str = "") -> str:
    """Read a setting from environment variables or Streamlit Secrets.

    Environment variables take precedence so Render/container deployments keep
    their existing contract. Streamlit deployments can use the same key names
    in st.secrets without committing credentials to the repository.
    """
    value = os.getenv(name)
    if value is not None and value.strip():
        return value.strip()

    try:
        import streamlit as st

        value = st.secrets.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()

        # Also accept conventional [auth] and [llm] sections in secrets.
        section_name = {
            "AUTH_USERNAME": "auth",
            "AUTH_PASSWORD_HASH": "auth",
            "AUTH_ROLE": "auth",
            "AUTH_SESSION_TTL_SECONDS": "auth",
            "AUTH_PBKDF2_ITERATIONS": "auth",
            "API_KEY": "llm",
            "GROQ_API_KEY": "llm",
            "LLM_PROVIDER": "llm",
            "LLM_MODEL": "llm",
            "API_BASE_URL": "llm",
            "OLLAMA_API_BASE": "llm",
            "OLLAMA_MODEL": "llm",
        }.get(name)
        if section_name:
            section = st.secrets.get(section_name)
            if isinstance(section, Mapping):
                value = section.get(name)
                if value is None:
                    short_name = name.removeprefix("AUTH_").removeprefix("LLM_")
                    value = section.get(short_name)
                if value is not None and str(value).strip():
                    return str(value).strip()
    except Exception:
        # Configuration lookup must remain usable in non-Streamlit test/CLI
        # contexts where Streamlit Secrets is unavailable.
        pass

    return default
