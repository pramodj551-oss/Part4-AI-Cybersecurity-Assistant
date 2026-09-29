"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Retriever Module
Version: 4.0
==========================================================

Retrieves the most relevant documents from the vector store.
"""

from __future__ import annotations

import logging
import time

from config.config import (
    SEARCH_TYPE,
    TOP_K
)
from src.vector_store import vector_store_manager


logger = logging.getLogger(__name__)


class RetrieverManager:
    """
    Handles document retrieval.
    """

    def __init__(
        self,
        search_type=SEARCH_TYPE,
        top_k=TOP_K
    ):

        self.search_type = search_type
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        request_id: str | None = None,
    ):
        """
        Retrieve relevant documents.
        """

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        retrieval_started = time.monotonic()
        logger.info("RETRIEVAL_PROBE start request_id=%s", request_id or "none")

        retriever = (
            vector_store_manager.as_retriever(
                search_type=self.search_type,
                k=self.top_k
            )
        )

        documents = retriever.invoke(query)

        logger.info(
            "RETRIEVAL_PROBE done request_id=%s documents=%d elapsed_ms=%d",
            request_id or "none",
            len(documents),
            int((time.monotonic() - retrieval_started) * 1000),
        )

        return documents

    def get_sources(
        self,
        documents
    ):
        """
        Extract unique document sources.
        """

        sources = []

        for document in documents:

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            if source not in sources:

                sources.append(source)

        return sources

    def retrieval_summary(
        self,
        documents
    ):
        """
        Generate retrieval statistics.
        """

        return {

            "retrieved_documents": len(documents),

            "sources": self.get_sources(
                documents
            )

        }


retriever_manager = RetrieverManager()
