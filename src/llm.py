"""OpenAI-compatible LLM client used by the RAG pipeline."""

from __future__ import annotations

import logging
import time

from openai import OpenAI

from config.config import API_BASE_URL, API_KEY, LLM_MODEL, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

LLM_TIMEOUT_SECONDS = 30.0
LLM_MAX_ATTEMPTS = 3
LLM_BACKOFF_SECONDS = 0.5
_RETRYABLE_ERROR_NAMES = frozenset(
    {"APITimeoutError", "APIConnectionError", "RateLimitError", "InternalServerError"}
)
SAFE_ERROR_MESSAGE = (
    "Unable to generate a response. Please verify the LLM service configuration."
)


class LLMManager:
    """Wrapper around an OpenAI-compatible LLM endpoint with bounded recovery."""

    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL,
            timeout=LLM_TIMEOUT_SECONDS,
            max_retries=0,
        )

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        return exc.__class__.__name__ in _RETRYABLE_ERROR_NAMES

    def generate(self, prompt: str, system_prompt: str | None = None, request_id: str | None = None) -> dict:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        request_started = time.monotonic()
        logger.info("LLM_PROBE request_start request_id=%s", request_id or "none")

        for attempt in range(LLM_MAX_ATTEMPTS):
            attempt_started = time.monotonic()
            logger.info(
                "LLM_PROBE attempt_start request_id=%s attempt=%d/%d",
                request_id or "none", attempt + 1, LLM_MAX_ATTEMPTS,
            )
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                content = response.choices[0].message.content or ""
                logger.info(
                    "LLM_PROBE response_done request_id=%s attempt=%d elapsed_ms=%d total_elapsed_ms=%d",
                    request_id or "none", attempt + 1,
                    int((time.monotonic() - attempt_started) * 1000),
                    int((time.monotonic() - request_started) * 1000),
                )
                return {
                    "answer": content.strip(),
                    "model": LLM_MODEL,
                    "finish_reason": response.choices[0].finish_reason,
                }
            except Exception as exc:
                logger.warning(
                    "LLM_PROBE attempt_error request_id=%s attempt=%d elapsed_ms=%d exception=%s",
                    request_id or "none", attempt + 1,
                    int((time.monotonic() - attempt_started) * 1000),
                    type(exc).__name__,
                )
                if not self._is_retryable(exc) or attempt == LLM_MAX_ATTEMPTS - 1:
                    logger.exception("LLM request failed.")
                    logger.info(
                        "LLM_PROBE final_error request_id=%s total_elapsed_ms=%d",
                        request_id or "none",
                        int((time.monotonic() - request_started) * 1000),
                    )
                    return {
                        "answer": SAFE_ERROR_MESSAGE,
                        "model": LLM_MODEL,
                        "finish_reason": "error",
                    }

                delay = LLM_BACKOFF_SECONDS * (2**attempt)
                logger.warning(
                    "Transient LLM provider failure; retrying attempt %d/%d after %.1fs.",
                    attempt + 2,
                    LLM_MAX_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)


llm_manager = LLMManager()
