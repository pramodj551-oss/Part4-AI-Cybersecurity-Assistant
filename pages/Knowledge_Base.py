"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Knowledge Base Page
Version: 4.0
==========================================================
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.config import KNOWLEDGE_BASE_DIR
from src.utils import file_size_mb


st.set_page_config(
    page_title="Knowledge Base",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Knowledge Base")

st.caption(
    "Browse documents available to the RAG system."
)

kb_path = Path(KNOWLEDGE_BASE_DIR)

if not kb_path.exists():

    st.warning("Knowledge base directory not found.")
    st.stop()

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".csv"
}

documents = []

for file in sorted(kb_path.rglob("*")):

    if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:

        documents.append(file)

st.metric(
    "Available Documents",
    len(documents)
)

search = st.text_input(
    "Search documents"
)

if search:

    documents = [

        doc for doc in documents

        if search.lower()
        in doc.name.lower()

    ]

if not documents:

    st.info("No matching documents found.")

else:

    for document in documents:

        with st.expander(document.name):

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Type:** {document.suffix.upper()}"
                )

                st.write(
                    f"**Size:** {file_size_mb(document)} MB"
                )

            with col2:

                st.write(
                    f"**Location:** {document.parent.name}"
                )

                st.write(
                    f"**Path:** `{document}`"
                )

st.sidebar.header("Knowledge Base")

st.sidebar.info(
    """
Supported document types:

- PDF

- TXT

- Markdown

- CSV
"""
  )
