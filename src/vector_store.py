"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Vector Store
Version: 4.0
==========================================================

Creates, loads and manages the FAISS vector database.
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from config.config import VECTOR_INDEX_PATH
from src.embeddings import embedding_manager


logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manage FAISS vector store.
    """

    def __init__(self):

        self.vector_store = None

    def create(
        self,
        documents: list[Document]
    ):
        """
        Create a new FAISS vector store.
        """

        if not documents:
            raise ValueError(
                "No documents supplied."
            )

        logger.info(
            "Creating FAISS index from %s documents.",
            len(documents)
        )

        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_manager.get_embedding_model()
        )

        return self.vector_store

    def save(
        self,
        path: str | Path = VECTOR_INDEX_PATH
    ):
        """
        Save FAISS index.
        """

        if self.vector_store is None:
            raise ValueError(
                "Vector store has not been created."
            )

        path = Path(path)

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.vector_store.save_local(
            str(path)
        )

        logger.info(
            "Vector store saved to %s",
            path
        )

    def load(
        self,
        path: str | Path = VECTOR_INDEX_PATH
    ):
        """
        Load existing FAISS index.
        """

        path = Path(path)

        self.vector_store = FAISS.load_local(
            str(path),
            embedding_manager.get_embedding_model(),
            allow_dangerous_deserialization=True
        )

        logger.info(
            "Vector store loaded from %s",
            path
        )

        return self.vector_store

    def add_documents(
        self,
        documents: list[Document]
    ):
        """
        Add documents to existing index.
        """

        if self.vector_store is None:
            raise ValueError(
                "Vector store not initialized."
            )

        self.vector_store.add_documents(
            documents
        )

        logger.info(
            "%s new documents added.",
            len(documents)
        )

    def as_retriever(
        self,
        search_type="similarity",
        k=5
    ):
        """
        Return LangChain retriever.
        """

        if self.vector_store is None:
            raise ValueError(
                "Vector store not initialized."
            )

        return self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={
                "k": k
            }
        )


vector_store_manager = VectorStoreManager()
