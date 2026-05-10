"""
Groq API Client with retry logic and error handling.
AI Developer 2 responsibility.
"""

import logging
import time
import json
from typing import Optional, Dict, Any, List
from groq import Groq, RateLimitError, APIError
import os

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Wrapper around Groq API with retry logic, error handling, and logging.
    Features:
    - 3-retry with exponential backoff
    - JSON response parsing
    - Error logging
    - Fallback template on failure
    """

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.max_retries = max_retries
        self.model = "llama-3.3-70b-versatile"
        self.last_response_time = 0.0

    def call(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
        system_message: str = "You are a helpful compliance training assistant.",
    ) -> Dict[str, Any]:
        """
        Call Groq API with retry logic and error handling.

        Args:
            prompt: User prompt/question
            temperature: 0.3 for factual, 0.7 for creative
            max_tokens: Maximum tokens in response
            system_message: System instructions

        Returns:
            {
                "success": bool,
                "content": str or None,
                "error": str or None,
                "is_fallback": bool,
                "response_time_ms": float,
                "model": str,
                "tokens_used": int or None
            }
        """
        start_time = time.time()
        attempt = 0

        while attempt < self.max_retries:
            try:
                logger.info(
                    f"Groq API call (attempt {attempt + 1}/{self.max_retries})"
                )

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                self.last_response_time = time.time() - start_time
                content = response.choices[0].message.content

                logger.info(f"Groq API call successful in {self.last_response_time:.2f}s")

                return {
                    "success": True,
                    "content": content,
                    "error": None,
                    "is_fallback": False,
                    "response_time_ms": self.last_response_time * 1000,
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens,
                }

            except RateLimitError as e:
                attempt += 1
                if attempt < self.max_retries:
                    wait_time = min(2 ** (attempt - 1), 8)
                    logger.warning(
                        f"Rate limit hit. Waiting {wait_time}s before retry #{attempt}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Rate limit exceeded after {self.max_retries} retries")
                    return self._fallback_response(
                        "Rate limit exceeded. Try again later.",
                        time.time() - start_time,
                    )

            except APIError as e:
                attempt += 1
                if attempt < self.max_retries:
                    wait_time = min(2 ** (attempt - 1), 8)
                    logger.warning(f"API error: {str(e)}. Retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API error after {self.max_retries} retries: {str(e)}")
                    return self._fallback_response(
                        "Service unavailable. Using cached response.", time.time() - start_time
                    )

            except Exception as e:
                logger.error(f"Unexpected error in Groq call: {type(e).__name__}: {str(e)}")
                return self._fallback_response(
                    f"Error: {str(e)}", time.time() - start_time
                )

        return self._fallback_response(
            "Unable to process request.", time.time() - start_time
        )

    def _fallback_response(self, error_msg: str, elapsed_time: float) -> Dict[str, Any]:
        """Return fallback response on failure."""
        return {
            "success": False,
            "content": "We are experiencing high demand. Please try again in a moment.",
            "error": error_msg,
            "is_fallback": True,
            "response_time_ms": elapsed_time * 1000,
            "model": self.model,
            "tokens_used": None,
        }

    def parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Safely parse JSON from response text.
        Groq may include markdown or extra text.
        """
        try:
            # Try direct parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
                return json.loads(json_str)
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
                return json.loads(json_str)
            else:
                logger.error(f"Could not parse JSON from: {response_text[:200]}")
                return None

    def get_last_response_time(self) -> float:
        """Get last API response time in seconds."""
        return self.last_response_time
