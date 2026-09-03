"""OpenAI-compatible LLM client used by the RAG pipeline."""

from __future__ import annotations

import logging

from openai import OpenAI

from config.config import API_BASE_URL, API_KEY, LLM_MODEL, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)


class LLMManager:
    """Wrapper around an OpenAI-compatible LLM endpoint."""

    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL,
        )

    def generate(self, prompt: str, system_prompt: str | None = None) -> dict:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            content = response.choices[0].message.content or ""
            return {
                "answer": content.strip(),
                "model": LLM_MODEL,
                "finish_reason": response.choices[0].finish_reason,
            }
        except Exception:
            logger.exception("LLM request failed.")
            return {
                "answer": "Unable to generate a response. Please verify the LLM service configuration.",
                "model": LLM_MODEL,
                "finish_reason": "error",
            }


llm_manager = LLMManager()
