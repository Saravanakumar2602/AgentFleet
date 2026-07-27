import logging
from backend.app.ai.base_llm import BaseLLM
from backend.app.ai.adapters.groq_adapter import GroqAdapter
from backend.app.ai.adapters.openai_adapter import OpenAIAdapter
from backend.app.ai.adapters.gemini_adapter import GeminiAdapter

logger = logging.getLogger("agentfleet.ai.llm_factory")

class LLMFactory:
    """
    Registry Factory to configure, map, and instantiate different LLM adapters.
    """
    _registry = {}

    @classmethod
    def register(cls, provider_name: str, adapter_cls) -> None:
        """
        Registers an adapter class for a provider name.
        """
        name_key = provider_name.lower().strip()
        cls._registry[name_key] = adapter_cls
        logger.info(f"Registered LLM provider: '{provider_name}' -> {adapter_cls.__name__}")

    @classmethod
    def get(cls, provider_name: str, **kwargs) -> BaseLLM:
        """
        Instantiates and returns the registered adapter class for a provider.
        Raises ValueError if the provider is not registered.
        """
        name_key = provider_name.lower().strip()
        adapter_cls = cls._registry.get(name_key)
        if not adapter_cls:
            logger.error(f"Requested unregistered provider: '{provider_name}'")
            raise ValueError(f"LLM provider '{provider_name}' is not registered.")
        
        logger.info(f"Instantiating adapter for provider: '{provider_name}'")
        return adapter_cls(**kwargs)

    @classmethod
    def list_models(cls) -> list[str]:
        """
        Lists all registered model provider names.
        """
        return list(cls._registry.keys())

# Auto-register core placeholders by default on module load
LLMFactory.register("groq", GroqAdapter)
LLMFactory.register("openai", OpenAIAdapter)
LLMFactory.register("gemini", GeminiAdapter)
