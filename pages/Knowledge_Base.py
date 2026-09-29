"""Knowledge Base page for the authoritative incident source and optional documents."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.config import (
    APP_ICON,
    APP_TITLE,
    INCIDENT_DATASET,
    KNOWLEDGE_BASE_DIR,
)
from src.auth import render_logout, require_auth
from src.data_loader import data_loader
from src.utils import file_size_mb


st.set_page_config(
    page_title="Knowledge Base",
    page_icon="📚",
    layout="wide",
)

require_auth()
render_logout()

st.title("📚 Knowledge Base")
st.caption(
    "Browse the authoritative incident dataset and optional supplemental "
    "documents available to the RAG system."
)

# The incident CSV is the repository's authoritative RAG source and is always
# expected in a normal deployment. The knowledge_base directory is optional:
# it is reserved for externally synchronized supplemental documents.
dataset_available = False
incident_count = 0

try:
    incidents = data_loader.load_csv(INCIDENT_DATASET)
    data_loader.validate(incidents)
    dataset_available = True
    incident_count = len(incidents)
except (FileNotFoundError, ValueError) as error:
    st.error(f"Authoritative incident dataset is unavailable: {error}")

st.metric("Incident Records", incident_count if dataset_available else 0)

if dataset_available:
    st.info(
        f"Authoritative RAG source: `{INCIDENT_DATASET.name}` "
        f"({incident_count} incident records)."
    )

    with st.expander("Preview incident knowledge"):
        st.dataframe(
            incidents.head(50),
            use_container_width=True,
            hide_index=True,
        )

# Optional supplemental document directory. A missing directory is not an
# error because the standalone deployment does not ship external Part 1
# knowledge-base artifacts.
kb_path = Path(KNOWLEDGE_BASE_DIR)
documents = []

if kb_path.is_dir():
    supported_extensions = {".pdf", ".txt", ".md", ".csv"}
    documents = [
        file
        for file in sorted(kb_path.rglob("*"))
        if file.is_file() and file.suffix.lower() in supported_extensions
    ]

    st.subheader("Supplemental Documents")
    search = st.text_input(
        "Search supplemental documents",
        key="knowledge_base_document_search",
    )

    if search.strip():
        documents = [
            doc
            for doc in documents
            if search.casefold() in doc.name.casefold()
        ]

    st.metric("Available Documents", len(documents))

    if not documents:
        st.info("No matching supplemental documents found.")
    else:
        for document in documents:
            with st.expander(document.name):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Type:** {document.suffix.upper()}")
                    st.write(f"**Size:** {file_size_mb(document)} MB")

                with col2:
                    st.write(f"**Location:** {document.parent.name}")
                    st.write(f"**Path:** `{document}`")
else:
    st.caption(
        "No supplemental knowledge_base directory is configured. "
        "The authoritative incident dataset remains the active knowledge source."
    )

if not dataset_available and not documents:
    st.stop()

st.sidebar.header("Knowledge Base")
st.sidebar.info(
    """
Primary source:

- Cybersecurity incident dataset

Optional supplemental types:

- PDF
- TXT
- Markdown
- CSV
"""
)
st.sidebar.caption(APP_TITLE)
st.sidebar.caption(f"{APP_ICON} Knowledge Base")
