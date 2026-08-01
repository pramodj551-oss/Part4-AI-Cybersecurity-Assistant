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
        query: str
    ):
        """
        Retrieve relevant documents.
        """

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        retriever = (
            vector_store_manager.as_retriever(
                search_type=self.search_type,
                k=self.top_k
            )
        )

        documents = retriever.invoke(query)

        logger.info(
            "Retrieved %s documents.",
            len(documents)
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
