"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Home Page
Version: 4.0
==========================================================
"""

from __future__ import annotations

import streamlit as st

from config.config import (
    APP_ICON,
    APP_TITLE
)


# ----------------------------------------------------------
# Page Configuration
# ----------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# Session State
# ----------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------------
# Sidebar
# ----------------------------------------------------------

with st.sidebar:

    st.title("🛡️ AI Cybersecurity Assistant")

    st.markdown("---")

    st.success("System Status: Online")

    st.markdown(
        """
### Navigation

Use the pages in the sidebar:

- 💬 Chat
- 📚 Knowledge Base
- 🔍 Incident Search
- ⚙️ Settings
"""
    )

    st.markdown("---")

    if st.button("🗑 Clear Chat History"):

        st.session_state.chat_history = []
        st.session_state.messages = []

        st.success("Chat history cleared.")

# ----------------------------------------------------------
# Main Page
# ----------------------------------------------------------

st.title(APP_TITLE)

st.caption(
    "Retrieval-Augmented Generation (RAG) for Cybersecurity Incident Response"
)

st.markdown("---")

st.header("🎯 Project Overview")

st.write(
    """
This application helps Security Operations Center (SOC) analysts
retrieve cybersecurity knowledge, search incidents,
and receive context-aware AI responses using
Retrieval-Augmented Generation (RAG).
"""
)

col1, col2 = st.columns(2)

with col1:

    st.subheader("✨ Features")

    st.markdown(
        """
- AI-powered cybersecurity assistant

- RAG-based document retrieval

- FAISS vector search

- Incident search

- SOP retrieval

- Knowledge base browser

- Multi-page Streamlit application
"""
    )

with col2:

    st.subheader("🛠 Technology Stack")

    st.markdown(
        """
- Python

- Streamlit

- LangChain

- FAISS

- Hugging Face Embeddings

- OpenAI-compatible APIs

- Pandas

- NumPy
"""
    )

st.markdown("---")

st.subheader("🚀 Quick Start")

st.info(
    """
1. Open **💬 Chat** to ask cybersecurity questions.

2. Browse documents in **📚 Knowledge Base**.

3. Search historical incidents in **🔍 Incident Search**.

4. Configure the application from **⚙️ Settings**.
"""
)

st.markdown("---")

st.success(
    "✅ AI-Powered Cybersecurity Incident Assistant is ready."
)

st.caption("Version 4.0")
