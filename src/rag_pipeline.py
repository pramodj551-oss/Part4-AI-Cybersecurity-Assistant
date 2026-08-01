"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
RAG Pipeline
Version: 4.0
==========================================================

Orchestrates the complete Retrieval-Augmented Generation
workflow.
"""

from __future__ import annotations

import logging

from src.llm import llm_manager
from src.prompt_builder import prompt_builder
from src.retriever import retriever_manager


logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end RAG orchestration.
    """

    def answer(
        self,
        question: str
    ) -> dict:
        """
        Execute the complete RAG workflow.

        Returns
        -------
        dict
            {
                "question": ...,
                "answer": ...,
                "sources": ...,
                "retrieved_documents": ...,
                "model": ...
            }
        """

        if not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        logger.info(
            "Starting RAG pipeline."
        )

        # -----------------------------------------
        # Retrieve Documents
        # -----------------------------------------

        documents = retriever_manager.retrieve(
            question
        )

        # -----------------------------------------
        # Build Prompt
        # -----------------------------------------

        prompt = prompt_builder.build_prompt(
            question=question,
            documents=documents
        )

        # -----------------------------------------
        # Generate Response
        # -----------------------------------------

        llm_response = llm_manager.generate(
            prompt
        )

        # -----------------------------------------
        # Sources
        # -----------------------------------------

        sources = prompt_builder.extract_sources(
            documents
        )

        logger.info(
            "RAG pipeline completed."
        )

        return {

            "question": question,

            "answer":
                llm_response["answer"],

            "sources": sources,

            "retrieved_documents":
                len(documents),

            "model":
                llm_response.get("model"),

            "finish_reason":
                llm_response.get("finish_reason")

        }


rag_pipeline = RAGPipeline()
