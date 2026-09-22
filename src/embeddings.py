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
import os

# Keep CPU-backed transformer/tokenizer runtimes from creating unnecessary
# thread pools on the 512 MB production instance. These variables must be set
# before importing the Hugging Face/PyTorch stack.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from config.config import EMBEDDING_MODEL


logger = logging.getLogger(__name__)


def _probe_log(message: str) -> None:
    """Emit embedding-model retrieval boundary evidence."""
    logger.info(message)
    print(f"STARTUP_PROBE: {message}", flush=True)


def _sanitize_exception(error: Exception) -> str:
    """Redact common secret-bearing values from diagnostic exception text."""
    message = str(error)
    for secret_name in ("api_key", "password", "token", "secret"):
        if secret_name in message.lower():
            message = f"[redacted {secret_name}]"
    return message[:500]


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

            _probe_log("embedding model cache miss")
            _probe_log(
                "embedding model configuration resolved: "
                f"model_name={EMBEDDING_MODEL}; device=cpu"
            )
            _probe_log("embedding model construction starting")

            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={
                        "device": "cpu"
                    },
                    encode_kwargs={
                        "normalize_embeddings": True,
                        "batch_size": 1,
                    }
                )
            except Exception as error:
                _probe_log(
                    "embedding model construction FAILED: "
                    f"exception={type(error).__name__}; "
                    f"message={_sanitize_exception(error)}"
                )
                raise

            _probe_log("embedding model construction completed")

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
