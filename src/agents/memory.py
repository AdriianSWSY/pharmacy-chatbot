"""
Thread-safe memory management for agents.
"""

from typing import Dict, Optional
from threading import Lock
from langchain.memory import ConversationBufferMemory
from langchain_core.memory import BaseMemory
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentMemory:
    """Thread-safe memory management for agents."""

    def __init__(self, session_timeout: int = 1800):
        """
        Initialize the memory manager.

        Args:
            session_timeout: Session timeout in seconds (default: 30 minutes)
        """
        self._memories: Dict[str, BaseMemory] = {}
        self._session_times: Dict[str, datetime] = {}
        self._lock = Lock()
        self.session_timeout = session_timeout

    def create_memory(self, session_id: str) -> ConversationBufferMemory:
        """
        Create a new memory instance for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationBufferMemory instance
        """
        with self._lock:
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
            self._memories[session_id] = memory
            self._session_times[session_id] = datetime.now()
            logger.info(f"Created memory for session: {session_id}")
            return memory

    def get_memory(self, session_id: str) -> Optional[ConversationBufferMemory]:
        """
        Get memory for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationBufferMemory instance if exists, None otherwise
        """
        with self._lock:
            if session_id in self._memories:
                # Update last access time
                self._session_times[session_id] = datetime.now()
                return self._memories[session_id]
            return None

    def get_or_create_memory(self, session_id: str) -> ConversationBufferMemory:
        """
        Get existing memory or create new one for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationBufferMemory instance
        """
        memory = self.get_memory(session_id)
        if memory is None:
            memory = self.create_memory(session_id)
        return memory

    def clear_memory(self, session_id: str) -> bool:
        """
        Clear memory for a specific session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if memory was cleared, False if session not found
        """
        with self._lock:
            if session_id in self._memories:
                if hasattr(self._memories[session_id], "clear"):
                    self._memories[session_id].clear()
                del self._memories[session_id]
                del self._session_times[session_id]
                logger.info(f"Cleared memory for session: {session_id}")
                return True
            return False

    def clear_expired_sessions(self):
        """Clear sessions that have exceeded the timeout period."""
        with self._lock:
            current_time = datetime.now()
            expired_sessions = []

            for session_id, last_access in self._session_times.items():
                if (current_time - last_access).seconds > self.session_timeout:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self._memories[session_id]
                del self._session_times[session_id]
                logger.info(f"Expired session cleared: {session_id}")

            if expired_sessions:
                logger.info(f"Cleared {len(expired_sessions)} expired sessions")

    def get_active_session_count(self) -> int:
        """
        Get the count of active sessions.

        Returns:
            Number of active sessions
        """
        with self._lock:
            return len(self._memories)

    def get_session_age(self, session_id: str) -> Optional[int]:
        """
        Get the age of a session in seconds.

        Args:
            session_id: Unique session identifier

        Returns:
            Age in seconds if session exists, None otherwise
        """
        with self._lock:
            if session_id in self._session_times:
                age = datetime.now() - self._session_times[session_id]
                return int(age.total_seconds())
            return None

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.

        Args:
            session_id: Unique session identifier

        Returns:
            True if session exists, False otherwise
        """
        with self._lock:
            return session_id in self._memories


# Global instance for singleton pattern
agent_memory = AgentMemory()
