"""FAISS vector-store management with artifact integrity verification."""

from __future__ import annotations

import hashlib
import logging
import os
import pickle
from pathlib import Path

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config.config import VECTOR_INDEX_PATH
from src.embeddings import embedding_manager

logger = logging.getLogger(__name__)


class _DeterministicSet(set):
    """Set with a stable pickle representation for string-valued metadata."""

    def __reduce_ex__(self, protocol):
        del protocol
        return (type(self), (tuple(sorted(self, key=repr)),))


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

    def create(self, documents: list[Document], ids: list[str] | None = None):
        if not documents:
            raise ValueError("No documents supplied.")
        if ids is not None:
            if len(ids) != len(documents):
                raise ValueError("ids must contain one ID for each document.")
            if len(set(ids)) != len(ids) or any(not item for item in ids):
                raise ValueError("ids must contain unique non-empty values.")
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_manager.get_embedding_model(),
            **({"ids": ids} if ids is not None else {}),
        )
        return self.vector_store

    @staticmethod
    def _canonicalize_document_state(document: Document) -> None:
        """Replace unordered Pydantic field sets with deterministic set objects."""
        fields_set = getattr(document, "__pydantic_fields_set__", None)
        if isinstance(fields_set, set) and not isinstance(fields_set, _DeterministicSet):
            object.__setattr__(document, "__pydantic_fields_set__", _DeterministicSet(fields_set))

    @classmethod
    def _write_deterministic_metadata(cls, path: Path) -> None:
        """Rewrite LangChain's pickle payload in a stable insertion order/protocol."""
        pickle_path = path / "index.pkl"
        with pickle_path.open("rb") as handle:
            docstore, index_to_docstore_id = pickle.load(handle)

        source_docs = getattr(docstore, "_dict", None)
        if not isinstance(source_docs, dict):
            raise RuntimeError("FAISS docstore does not expose a serializable document mapping.")

        ordered_ids = [index_to_docstore_id[key] for key in sorted(index_to_docstore_id)]
        ordered_docs = {}
        for doc_id in ordered_ids:
            document = source_docs[doc_id]
            cls._canonicalize_document_state(document)
            ordered_docs[doc_id] = document

        canonical_docstore = InMemoryDocstore(ordered_docs)
        canonical_mapping = {
            int(key): index_to_docstore_id[key]
            for key in sorted(index_to_docstore_id)
        }

        with pickle_path.open("wb") as handle:
            pickle.dump(
                (canonical_docstore, canonical_mapping),
                handle,
                protocol=4,
            )

    def save(self, path: str | Path = VECTOR_INDEX_PATH):
        if self.vector_store is None:
            raise ValueError("Vector store has not been created.")

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(path))
        self._write_deterministic_metadata(path)

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
