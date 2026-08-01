"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Prompt Builder
Version: 4.0
==========================================================

Builds prompts for Retrieval-Augmented Generation.
"""

from __future__ import annotations

import logging
from pathlib import Path

from config.config import PROMPTS_DIR

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds prompts for the LLM.
    """

    def __init__(self):

        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        Load system prompt from file.
        """

        prompt_file = Path(PROMPTS_DIR) / "system_prompt.txt"

        if prompt_file.exists():

            logger.info(
                "Loaded system prompt."
            )

            return prompt_file.read_text(
                encoding="utf-8"
            )

        logger.warning(
            "System prompt not found. Using default."
        )

        return (
            "You are an AI-powered cybersecurity assistant. "
            "Answer only using the supplied context. "
            "If the answer is not available in the context, "
            "clearly state that you do not know."
        )

    def build_context(
        self,
        documents
    ) -> str:
        """
        Merge retrieved documents.
        """

        return "\n\n".join(
            document.page_content
            for document in documents
        )

    def build_prompt(
        self,
        question: str,
        documents
    ) -> str:
        """
        Build the final prompt.
        """

        context = self.build_context(
            documents
        )

        prompt = f"""
{self.system_prompt}

==================================================

Context

{context}

==================================================

User Question

{question}

==================================================

Instructions

1. Answer only from the provided context.
2. If the answer is unavailable, say so.
3. Be concise and technically accurate.
4. Mention incident response steps where applicable.
5. Do not invent facts.

==================================================

Answer:
"""

        logger.info(
            "Prompt generated."
        )

        return prompt

    def extract_sources(
        self,
        documents
    ):
        """
        Return unique source names.
        """

        sources = []

        for document in documents:

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            if source not in sources:

                sources.append(source)

        return sources


prompt_builder = PromptBuilder()
