import os
import sys

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.ai.llm_factory import LLMFactory
from backend.app.ai.adapters.groq_adapter import GroqAdapter
from backend.app.ai.adapters.openai_adapter import OpenAIAdapter
from backend.app.ai.adapters.gemini_adapter import GeminiAdapter

def test_llm_factory():
    print("Testing LLMFactory registry maps...")
    
    # 1. Verify registered models list
    models = LLMFactory.list_models()
    print(f"Registered models in factory: {models}")
    assert "groq" in models
    assert "openai" in models
    assert "gemini" in models
    
    # 2. Get and verify Groq Adapter
    groq_instance = LLMFactory.get("groq", api_key="test-key-123")
    assert isinstance(groq_instance, GroqAdapter)
    assert groq_instance.api_key == "test-key-123"
    assert groq_instance.health_check() is True
    
    # 3. Get and verify OpenAI Adapter
    openai_instance = LLMFactory.get("openai", api_key="openai-key")
    assert isinstance(openai_instance, OpenAIAdapter)
    
    # 4. Get and verify Gemini Adapter
    gemini_instance = LLMFactory.get("gemini", api_key="gemini-key")
    assert isinstance(gemini_instance, GeminiAdapter)

    # 5. Invalid provider exception check
    try:
        LLMFactory.get("non-existent-provider")
        print("❌ Factory lookup check failed: did not raise ValueError.")
        assert False
    except ValueError:
        print("Correctly raised ValueError on invalid model provider.")

    # 6. Test generation calls
    gen_out = groq_instance.generate("Hello world")
    assert "[Groq" in gen_out
    assert "Hello world" in gen_out
    
    chat_out = groq_instance.chat([{"role": "user", "content": "How are you?"}])
    assert "Simulated reply to: 'How are you?'" in chat_out

    print("LLMFactory tests executed successfully!")

if __name__ == "__main__":
    test_llm_factory()
