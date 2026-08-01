"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Response Generator
Version: 4.0
==========================================================

Formats RAG pipeline output into a consistent response
structure for the Streamlit application or API.
"""

from __future__ import annotations

from datetime import datetime


class ResponseGenerator:
    """
    Formats RAG responses.
    """

    def generate(
        self,
        rag_result: dict
    ) -> dict:
        """
        Convert raw RAG output into a standardized response.
        """

        return {

            "success": True,

            "timestamp": datetime.utcnow().isoformat(),

            "question": rag_result.get(
                "question",
                ""
            ),

            "answer": rag_result.get(
                "answer",
                "No answer generated."
            ),

            "sources": rag_result.get(
                "sources",
                []
            ),

            "retrieved_documents": rag_result.get(
                "retrieved_documents",
                0
            ),

            "model": rag_result.get(
                "model",
                "Unknown"
            ),

            "finish_reason": rag_result.get(
                "finish_reason",
                "unknown"
            )

        }

    def generate_error(
        self,
        message: str
    ) -> dict:
        """
        Standard error response.
        """

        return {

            "success": False,

            "timestamp": datetime.utcnow().isoformat(),

            "answer": "",

            "error": message,

            "sources": [],

            "retrieved_documents": 0

        }

    def format_sources(
        self,
        sources: list[str]
    ) -> str:
        """
        Convert source list into readable text.
        """

        if not sources:
            return "No sources available."

        return "\n".join(
            f"- {source}"
            for source in sources
        )


response_generator = ResponseGenerator()
