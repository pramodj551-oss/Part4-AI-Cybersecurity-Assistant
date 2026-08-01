"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Settings Page
Version: 4.0
==========================================================
"""

from __future__ import annotations

import streamlit as st

from config.config import (
    APP_TITLE,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_PROVIDER,
    SEARCH_TYPE,
    TOP_K,
    TEMPERATURE,
    MAX_TOKENS
)

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Application Settings")

st.caption(
    "Current configuration of the AI-Powered Cybersecurity Incident Assistant."
)

# ----------------------------------------------------------
# Model Configuration
# ----------------------------------------------------------

st.header("🤖 Language Model")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Provider",
        LLM_PROVIDER
    )

    st.metric(
        "Model",
        LLM_MODEL
    )

with col2:

    st.metric(
        "Temperature",
        TEMPERATURE
    )

    st.metric(
        "Max Tokens",
        MAX_TOKENS
    )

# ----------------------------------------------------------
# Embedding Configuration
# ----------------------------------------------------------

st.header("🧠 Embedding Model")

st.info(
    EMBEDDING_MODEL
)

# ----------------------------------------------------------
# Retrieval Configuration
# ----------------------------------------------------------

st.header("📚 Retrieval Settings")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Top-K",
        TOP_K
    )

with col2:

    st.metric(
        "Chunk Size",
        CHUNK_SIZE
    )

with col3:

    st.metric(
        "Chunk Overlap",
        CHUNK_OVERLAP
    )

st.write(
    f"**Search Type:** {SEARCH_TYPE}"
)

# ----------------------------------------------------------
# Application Information
# ----------------------------------------------------------

st.header("ℹ️ Application")

st.write(f"**Application:** {APP_TITLE}")
st.write("**Version:** 4.0")
st.write("**Framework:** Streamlit")
st.write("**Vector Store:** FAISS")
st.write("**RAG Framework:** LangChain")

# ----------------------------------------------------------
# Environment Status
# ----------------------------------------------------------

st.header("✅ System Status")

status = {
    "LLM Configuration": "Ready",
    "Embedding Model": "Configured",
    "Vector Store": "Available",
    "Retriever": "Available",
    "RAG Pipeline": "Ready"
}

st.json(status)

# ----------------------------------------------------------
# About
# ----------------------------------------------------------

with st.expander("About"):

    st.markdown(
        """
This application demonstrates a production-style
Retrieval-Augmented Generation (RAG) pipeline for
cybersecurity incident response.

Features include:

- AI Chat Assistant
- Knowledge Base Search
- FAISS Vector Database
- LangChain Integration
- OpenAI-compatible LLM Support
- Streamlit User Interface
"""
)
