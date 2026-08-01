"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Embeddings Module
Version: 4.0
==========================================================

Loads and manages the embedding model used by the
RAG pipeline.
"""

from __future__ import annotations

import logging

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from config.config import EMBEDDING_MODEL


logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Handles embedding model loading and embedding generation.
    """

    def __init__(self):

        self._embeddings = None

    @property
    def embeddings(self):
        """
        Lazy-load embedding model.
        """

        if self._embeddings is None:

            logger.info(
                "Loading embedding model: %s",
                EMBEDDING_MODEL
            )

            self._embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={
                    "device": "cpu"
                },
                encode_kwargs={
                    "normalize_embeddings": True
                }
            )

        return self._embeddings

    def embed_documents(
        self,
        documents: list[Document]
    ) -> list[list[float]]:
        """
        Generate embeddings for LangChain documents.
        """

        texts = [
            doc.page_content
            for doc in documents
        ]

        logger.info(
            "Embedding %s documents.",
            len(texts)
        )

        return self.embeddings.embed_documents(
            texts
        )

    def embed_query(
        self,
        query: str
    ) -> list[float]:
        """
        Generate embedding for a user query.
        """

        logger.info(
            "Embedding query."
        )

        return self.embeddings.embed_query(
            query
        )

    def get_embedding_model(self):
        """
        Return the initialized embedding model.
        """

        return self.embeddings


embedding_manager = EmbeddingManager()
