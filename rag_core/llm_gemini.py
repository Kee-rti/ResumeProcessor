import logging
import os

import truststore

# Must happen before the Gemini SDK creates its HTTP clients.
truststore.inject_into_ssl()

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiLLM:
    """Small wrapper around the Gemini Developer API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Set it in the environment "
                "or pass api_key explicitly."
            )

        self.model = model or os.getenv(
            "GEMINI_MODEL", "gemini-2.5-flash-lite"
        )
        self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        text = response.text
        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return text.strip()
