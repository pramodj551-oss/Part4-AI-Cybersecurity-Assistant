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
import time

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


def _process_memory_mib() -> tuple[float | None, float | None]:
    """Return current RSS and peak RSS from Linux procfs, in MiB."""
    try:
        current_kib = None
        peak_kib = None
        with open("/proc/self/status", "r", encoding="utf-8") as status_file:
            for line in status_file:
                if line.startswith("VmRSS:"):
                    current_kib = int(line.split()[1])
                elif line.startswith("VmHWM:"):
                    peak_kib = int(line.split()[1])

        current_mib = current_kib / 1024 if current_kib is not None else None
        peak_mib = peak_kib / 1024 if peak_kib is not None else None
        return current_mib, peak_mib
    except (OSError, ValueError, IndexError):
        return None, None


def _memory_probe_log(stage: str, baseline_peak_mib: float | None = None) -> None:
    """Emit RSS/peak-RSS evidence without changing model behavior."""
    rss_mib, peak_mib = _process_memory_mib()
    fields = [f"stage={stage}"]
    if rss_mib is not None:
        fields.append(f"rss_mib={rss_mib:.1f}")
    if peak_mib is not None:
        fields.append(f"peak_rss_mib={peak_mib:.1f}")
    if baseline_peak_mib is not None and peak_mib is not None:
        fields.append(f"peak_delta_mib={peak_mib - baseline_peak_mib:.1f}")
    _probe_log("embedding memory " + "; ".join(fields))


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
            _, baseline_peak_mib = _process_memory_mib()
            _memory_probe_log("before_construction", baseline_peak_mib)
            construction_started = time.monotonic()

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
                _memory_probe_log("construction_exception", baseline_peak_mib)
                _probe_log(
                    "embedding model construction FAILED: "
                    f"exception={type(error).__name__}; "
                    f"message={_sanitize_exception(error)}"
                )
                raise

            _memory_probe_log("after_construction", baseline_peak_mib)
            _probe_log(
                "embedding model construction completed; "
                f"elapsed_ms={int((time.monotonic() - construction_started) * 1000)}"
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
