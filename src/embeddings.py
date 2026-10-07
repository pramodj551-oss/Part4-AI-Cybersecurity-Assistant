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
import threading
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


def _read_rss_bytes() -> int | None:
    """Return current process RSS from Linux procfs without adding a dependency."""
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except (FileNotFoundError, OSError, ValueError, IndexError):
        return None
    return None


def _sample_peak_rss(stop_event: threading.Event, peak_holder: dict[str, int | None]) -> None:
    """Sample RSS during model construction so short-lived peaks are observable."""
    peak = _read_rss_bytes()
    while not stop_event.wait(0.05):
        rss = _read_rss_bytes()
        if rss is not None and (peak is None or rss > peak):
            peak = rss
    final_rss = _read_rss_bytes()
    if final_rss is not None and (peak is None or final_rss > peak):
        peak = final_rss
    peak_holder["peak"] = peak


def _rss_mb(value: int | None) -> str:
    return "unknown" if value is None else f"{value / (1024 * 1024):.1f}"


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
            construction_started = time.monotonic()
            rss_before = _read_rss_bytes()
            _probe_log(f"embedding model RSS-before; rss_mb={_rss_mb(rss_before)}")
            rss_stop = threading.Event()
            rss_peak = {"peak": rss_before}
            rss_sampler = threading.Thread(target=_sample_peak_rss, args=(rss_stop, rss_peak), name="embedding-rss-probe", daemon=True)
            rss_sampler.start()
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True, "batch_size": 1},
                )
            except Exception as error:
                rss_stop.set()
                rss_sampler.join(timeout=1)
                rss_after = _read_rss_bytes()
                _probe_log(
                    "embedding model construction FAILED: "
                    f"exception={type(error).__name__}; message={_sanitize_exception(error)}; "
                    f"rss_after_mb={_rss_mb(rss_after)}; peak_rss_mb={_rss_mb(rss_peak.get('peak'))}"
                )
                raise
            finally:
                rss_stop.set()
                rss_sampler.join(timeout=1)
            rss_after = _read_rss_bytes()
            peak_rss = rss_peak.get("peak")
            _probe_log(f"embedding model RSS-after; rss_mb={_rss_mb(rss_after)}")
            _probe_log(f"embedding model peak RSS; peak_rss_mb={_rss_mb(peak_rss)}")
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
