"""End-to-end retrieval-augmented generation pipeline."""

from __future__ import annotations

import logging
import time

from src.concurrency import RAGConcurrencyGuard
from src.llm import llm_manager
from src.prompt_builder import prompt_builder
from src.retriever import retriever_manager

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieve evidence, build a safe prompt, and generate an answer."""

    def __init__(self, concurrency_guard: RAGConcurrencyGuard | None = None) -> None:
        self.concurrency_guard = concurrency_guard or RAGConcurrencyGuard()

    def answer(self, question: str, request_id: str | None = None) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        # Only the expensive retrieval/LLM path is guarded. Health/readiness
        # endpoints and lightweight application startup checks are unaffected.
        with self.concurrency_guard:
            pipeline_started = time.monotonic()
            logger.info("RAG_PROBE request_start request_id=%s", request_id or "none")
            retrieval_started = time.monotonic()
            logger.info("RAG_PROBE retrieval_start request_id=%s", request_id or "none")
            documents = retriever_manager.retrieve(question, request_id=request_id)
            logger.info(
                "RAG_PROBE retrieval_done request_id=%s documents=%d elapsed_ms=%d",
                request_id or "none",
                len(documents),
                int((time.monotonic() - retrieval_started) * 1000),
            )
            prompt_started = time.monotonic()
            prompt = prompt_builder.build_prompt(question, documents)
            logger.info(
                "RAG_PROBE prompt_done request_id=%s elapsed_ms=%d",
                request_id or "none",
                int((time.monotonic() - prompt_started) * 1000),
            )
            llm_started = time.monotonic()
            logger.info("RAG_PROBE llm_start request_id=%s", request_id or "none")
            llm_response = llm_manager.generate(
                prompt,
                system_prompt=prompt_builder.system_prompt,
                request_id=request_id,
            )
            logger.info(
                "RAG_PROBE llm_done request_id=%s elapsed_ms=%d",
                request_id or "none",
                int((time.monotonic() - llm_started) * 1000),
            )
            logger.info(
                "RAG_PROBE request_done request_id=%s elapsed_ms=%d",
                request_id or "none",
                int((time.monotonic() - pipeline_started) * 1000),
            )

        return {
            "question": question,
            "answer": llm_response["answer"],
            "sources": prompt_builder.extract_sources(documents),
            "retrieved_documents": len(documents),
            "model": llm_response.get("model"),
            "finish_reason": llm_response.get("finish_reason"),
        }


rag_pipeline = RAGPipeline()
