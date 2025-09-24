"""
Base conversational agent abstract class.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain_core.memory import BaseMemory
import logging

logger = logging.getLogger(__name__)


class ConversationalAgent(ABC):
    """Abstract base class for all conversational agents."""

    def __init__(self, session_id: str, memory: Optional[BaseMemory] = None):
        """
        Initialize the conversational agent.

        Args:
            session_id: Unique session identifier
            memory: Optional memory instance, creates ConversationBufferMemory if None
        """
        self.session_id = session_id
        self.memory = memory or ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.metadata: Dict[str, Any] = {}
        logger.info(f"Initialized {self.__class__.__name__} for session {session_id}")

    @abstractmethod
    async def process_message(self, message: str) -> str:
        """
        Process an incoming message and return a response.

        Args:
            message: The user's message

        Returns:
            The agent's response
        """
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        """
        Get the type of agent.

        Returns:
            String identifying the agent type
        """
        pass

    def get_conversation_history(self) -> list:
        """
        Get the conversation history.

        Returns:
            List of conversation messages
        """
        if hasattr(self.memory, "chat_memory"):
            return self.memory.chat_memory.messages
        return []

    def clear_memory(self):
        """Clear the conversation memory."""
        if hasattr(self.memory, "clear"):
            self.memory.clear()
        logger.info(f"Cleared memory for session {self.session_id}")

    def update_metadata(self, key: str, value: Any):
        """
        Update agent metadata.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
