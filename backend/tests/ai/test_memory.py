import os
import sys

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.ai.memory import ConversationMemory

def test_conversation_memory():
    print("Testing ConversationMemory lifecycle hooks...")
    
    memory = ConversationMemory()
    
    # 1. Assert initial state empty
    assert len(memory.history()) == 0
    
    # 2. Add message and assert history contents
    memory.add("user", "Hello assistant")
    history = memory.history()
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello assistant"
    
    # 3. Add replies and verify ordering
    memory.add("assistant", "How can I help you today?")
    history_after = memory.history()
    assert len(history_after) == 2
    assert history_after[1]["role"] == "assistant"
    
    # 4. Clear memory and verify empty
    memory.clear()
    assert len(memory.history()) == 0
    print("ConversationMemory tests executed successfully!")

if __name__ == "__main__":
    test_conversation_memory()
