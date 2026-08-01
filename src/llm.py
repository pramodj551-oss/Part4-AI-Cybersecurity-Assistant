"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
LLM Module
Version: 4.0
==========================================================

OpenAI-compatible LLM client.
Supports providers such as OpenAI, Groq and other
OpenAI-compatible APIs.
"""

from __future__ import annotations

import logging

from openai import OpenAI

from config.config import (
    API_BASE_URL,
    API_KEY,
    LLM_MODEL,
    MAX_TOKENS,
    TEMPERATURE
)

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Wrapper around an OpenAI-compatible client.
    """

    def __init__(self):

        self.client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL or None
        )

    def generate(
        self,
        prompt: str
    ) -> dict:
        """
        Generate an LLM response.
        """

        try:

            response = self.client.chat.completions.create(

                model=LLM_MODEL,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=TEMPERATURE,

                max_tokens=MAX_TOKENS
            )

            answer = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            logger.info(
                "LLM response generated."
            )

            return {

                "answer": answer,

                "model": LLM_MODEL,

                "finish_reason":
                response.choices[0].finish_reason

            }

        except Exception as error:

            logger.exception(
                "LLM request failed."
            )

            return {

                "answer":
                "Unable to generate a response.",

                "model": LLM_MODEL,

                "finish_reason": "error",

                "error": str(error)

            }


llm_manager = LLMManager()
