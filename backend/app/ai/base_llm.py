from abc import ABC, abstractmethod

class BaseLLM(ABC):
    """
    Abstract Base Class for LLM providers and adapters.
    Unifies interaction signatures for different providers.
    """
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates text output for a single textual prompt.
        """
        pass

    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Runs a chat completion using a structured conversation history format:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Performs connectivity or health checks against the provider endpoint.
        Returns True if operational, False otherwise.
        """
        pass
