import logging

logger = logging.getLogger("agentfleet.ai.memory")

class ConversationMemory:
    """
    Session-level conversation memory manager storing messages in system memory.
    """
    def __init__(self):
        self._history = []

    def add(self, role: str, content: str) -> None:
        """
        Appends a message to the conversation history list.
        """
        msg = {"role": role.strip().lower(), "content": content.strip()}
        self._history.append(msg)
        logger.info(f"Added message to memory: role={role}")

    def history(self) -> list[dict]:
        """
        Retrieves all messages recorded in history.
        """
        return list(self._history)

    def clear(self) -> None:
        """
        Flushes the current conversation history.
        """
        self._history.clear()
        logger.info("Conversation memory cleared.")
