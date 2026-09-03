"""FAISS vector-store management with artifact integrity verification."""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config.config import VECTOR_INDEX_PATH
from src.embeddings import embedding_manager

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manage FAISS indexes without loading unverified pickle artifacts."""

    def __init__(self):
        self.vector_store = None

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def create(self, documents: list[Document]):
        if not documents:
            raise ValueError("No documents supplied.")
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_manager.get_embedding_model(),
        )
        return self.vector_store

    def save(self, path: str | Path = VECTOR_INDEX_PATH):
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(path))

        pickle_path = path / "index.pkl"
        digest = self._sha256(pickle_path)
        logger.info("FAISS artifact SHA-256: %s", digest)
        return digest

    def load(self, path: str | Path = VECTOR_INDEX_PATH):
        """Load only an artifact whose SHA-256 is explicitly allow-listed.

        LangChain's FAISS local loader uses pickle for its metadata. Therefore
        dangerous deserialization is enabled only after the expected hash is
        supplied out-of-band via FAISS_INDEX_PKL_SHA256.
        """
        path = Path(path)
        pickle_path = path / "index.pkl"
        index_path = path / "index.faiss"

        if not pickle_path.is_file() or not index_path.is_file():
            raise FileNotFoundError(
                f"FAISS index is incomplete: expected {index_path} and {pickle_path}"
            )

        expected = os.getenv("FAISS_INDEX_PKL_SHA256", "").strip().lower()
        if not expected or len(expected) != 64:
            raise RuntimeError(
                "FAISS_INDEX_PKL_SHA256 must be configured before loading a local FAISS index."
            )

        actual = self._sha256(pickle_path)
        if actual != expected:
            raise RuntimeError("FAISS index integrity check failed; refusing deserialization.")

        self.vector_store = FAISS.load_local(
            str(path),
            embedding_manager.get_embedding_model(),
            allow_dangerous_deserialization=True,
        )
        logger.info("Verified FAISS vector store loaded from %s", path)
        return self.vector_store

    def add_documents(self, documents: list[Document]):
        if self.vector_store is None:
            raise ValueError("Vector store not initialized.")
        if not documents:
            return
        self.vector_store.add_documents(documents)

    def as_retriever(self, search_type="similarity", k=5):
        if self.vector_store is None:
            raise ValueError("Vector store not initialized.")
        if not isinstance(k, int) or not 1 <= k <= 50:
            raise ValueError("k must be an integer between 1 and 50.")
        return self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k},
        )


vector_store_manager = VectorStoreManager()
