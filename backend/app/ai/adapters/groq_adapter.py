import os
import json
import logging
from groq import Groq

from backend.app.ai.base_llm import BaseLLM
from backend.app.shared.exceptions import AIParserException

logger = logging.getLogger("agentfleet.ai.adapters.groq_adapter")

class GroqAdapter(BaseLLM):
    """
    Groq API client adapter implementing BaseLLM.
    Orchestrates completions, conversation histories, health checks, 
    and handles invalid JSON retries and exception translations.
    """
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile", **kwargs):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model
        self.config = kwargs
        
        # Instantiate the client (use empty/mock string if missing to support offline unit tests)
        self.client = Groq(api_key=self.api_key or "mock-key")
        logger.info(f"GroqAdapter initialized with model: '{self.model}'")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates text output for a single textual prompt.
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Runs a chat completion using the Groq SDK.
        If a JSON format is expected (detected via prompts content),
        validates the output structure, retrying once on JSON failures.
        """
        # Determine if JSON is expected by scanning message contents
        is_json_expected = False
        for msg in messages:
            content_lower = str(msg.get("content", "")).lower()
            if "json" in content_lower:
                is_json_expected = True
                break

        def _execute_completion() -> str:
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    **kwargs
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq API call execution failed: {e}")
                raise e

        # First Attempt
        content = _execute_completion()

        if is_json_expected:
            cleaned_content = self._clean_json_content(content)
            try:
                json.loads(cleaned_content)
                return cleaned_content
            except json.JSONDecodeError as err:
                logger.warning(f"First attempt returned invalid JSON. Error: {err}. Retrying once...")
                
                # Second Attempt (Retry once)
                content = _execute_completion()
                cleaned_content = self._clean_json_content(content)
                try:
                    json.loads(cleaned_content)
                    return cleaned_content
                except json.JSONDecodeError as final_err:
                    logger.error(f"Second attempt also returned invalid JSON. Error: {final_err}")
                    raise AIParserException(f"Failed to generate valid JSON: {content}")

        return content

    def health_check(self) -> bool:
        """
        Performs connectivity or health checks by querying the models list.
        """
        if not self.api_key or self.api_key == "mock-key":
            logger.warning("Groq health check skipped: No valid GROQ_API_KEY configured.")
            return False
        try:
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Groq connectivity check failed: {e}")
            return False

    def _clean_json_content(self, content: str) -> str:
        """
        Extracts raw JSON content from markdown wrappers if present.
        """
        stripped = content.strip()
        if stripped.startswith("```json"):
            stripped = stripped[7:]
        elif stripped.startswith("```"):
            stripped = stripped[3:]
        if stripped.endswith("```"):
            stripped = stripped[:-3]
        return stripped.strip()
