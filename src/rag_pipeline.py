"""End-to-end retrieval-augmented generation pipeline."""

from __future__ import annotations

import logging

from src.concurrency import RAGConcurrencyGuard
from src.llm import llm_manager
from src.prompt_builder import prompt_builder
from src.retriever import retriever_manager

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieve evidence, build a safe prompt, and generate an answer."""

    def __init__(self, concurrency_guard: RAGConcurrencyGuard | None = None) -> None:
        self.concurrency_guard = concurrency_guard or RAGConcurrencyGuard()

    def answer(self, question: str) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        # Only the expensive retrieval/LLM path is guarded. Health/readiness
        # endpoints and lightweight application startup checks are unaffected.
        with self.concurrency_guard:
            documents = retriever_manager.retrieve(question)
            prompt = prompt_builder.build_prompt(question, documents)
            llm_response = llm_manager.generate(
                prompt,
                system_prompt=prompt_builder.system_prompt,
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
