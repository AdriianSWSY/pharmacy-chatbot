"""
WebSocket connection management module with proper error handling.
"""

from typing import Dict, Optional, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and routing."""

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        # Track which connections are known to be active
        self.active_sessions: Set[str] = set()

    async def connect(self, websocket_id: str, websocket: WebSocket):
        """
        Accept and store a WebSocket connection.

        Args:
            websocket_id: Unique identifier for the connection
            websocket: WebSocket instance
        """
        try:
            await websocket.accept()
            self.active_connections[websocket_id] = websocket
            self.active_sessions.add(websocket_id)
            logger.info(f"WebSocket connected: {websocket_id}")
        except Exception as e:
            logger.error(f"Error accepting WebSocket {websocket_id}: {e}")
            raise

    async def disconnect(self, websocket_id: str):
        """
        Remove a WebSocket connection from active connections.

        Args:
            websocket_id: Unique identifier for the connection
        """
        # Remove from active sessions first
        self.active_sessions.discard(websocket_id)

        # Then remove from connections
        if websocket_id in self.active_connections:
            del self.active_connections[websocket_id]
            logger.info(f"WebSocket disconnected: {websocket_id}")

    async def send_message(self, websocket_id: str, message: dict) -> bool:
        """
        Send a JSON message to a specific WebSocket connection.

        Args:
            websocket_id: Unique identifier for the connection
            message: Dictionary to send as JSON

        Returns:
            True if message was sent successfully, False otherwise
        """
        # Check if session is marked as active
        if websocket_id not in self.active_sessions:
            logger.debug(f"WebSocket {websocket_id} not in active sessions")
            return False

        if websocket_id not in self.active_connections:
            logger.debug(f"WebSocket {websocket_id} not in active connections")
            self.active_sessions.discard(websocket_id)
            return False

        try:
            websocket = self.active_connections[websocket_id]
            await websocket.send_json(message)
            return True
        except RuntimeError as e:
            # Handle the specific "WebSocket is not connected" error
            error_msg = str(e).lower()
            if "websocket" in error_msg and "not connected" in error_msg:
                logger.debug(f"WebSocket {websocket_id} is not connected: {e}")
            else:
                logger.error(f"Runtime error sending to {websocket_id}: {e}")
            await self.disconnect(websocket_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to {websocket_id}: {e}")
            await self.disconnect(websocket_id)
            return False

    async def send_text(self, websocket_id: str, text: str) -> bool:
        """
        Send a text message to a specific WebSocket connection.

        Args:
            websocket_id: Unique identifier for the connection
            text: Text message to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        # Check if session is marked as active
        if websocket_id not in self.active_sessions:
            logger.debug(f"WebSocket {websocket_id} not in active sessions")
            return False

        if websocket_id not in self.active_connections:
            logger.debug(f"WebSocket {websocket_id} not in active connections")
            self.active_sessions.discard(websocket_id)
            return False

        try:
            websocket = self.active_connections[websocket_id]
            await websocket.send_text(text)
            return True
        except RuntimeError as e:
            # Handle the specific "WebSocket is not connected" error
            error_msg = str(e).lower()
            if "websocket" in error_msg and "not connected" in error_msg:
                logger.debug(f"WebSocket {websocket_id} is not connected: {e}")
            else:
                logger.error(f"Runtime error sending to {websocket_id}: {e}")
            await self.disconnect(websocket_id)
            return False
        except Exception as e:
            logger.error(f"Error sending text to {websocket_id}: {e}")
            await self.disconnect(websocket_id)
            return False

    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        """
        Broadcast a message to all connected WebSockets.

        Args:
            message: Dictionary to broadcast as JSON
            exclude: Optional websocket_id to exclude from broadcast
        """
        disconnected = []

        # Use a copy of the sessions to avoid modification during iteration
        for websocket_id in list(self.active_sessions):
            if websocket_id == exclude:
                continue

            if websocket_id not in self.active_connections:
                disconnected.append(websocket_id)
                continue

            try:
                websocket = self.active_connections[websocket_id]
                await websocket.send_json(message)
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "websocket" in error_msg and "not connected" in error_msg:
                    logger.debug(
                        f"WebSocket {websocket_id} disconnected during broadcast"
                    )
                else:
                    logger.error(f"Runtime error broadcasting to {websocket_id}: {e}")
                disconnected.append(websocket_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {websocket_id}: {e}")
                disconnected.append(websocket_id)

        # Clean up disconnected connections
        for websocket_id in disconnected:
            await self.disconnect(websocket_id)

    def get_connection(self, websocket_id: str) -> Optional[WebSocket]:
        """
        Get a specific WebSocket connection.

        Args:
            websocket_id: Unique identifier for the connection

        Returns:
            WebSocket instance if exists, None otherwise
        """
        return self.active_connections.get(websocket_id)

    def is_connected(self, websocket_id: str) -> bool:
        """
        Check if a WebSocket session is active.

        Args:
            websocket_id: Unique identifier for the connection

        Returns:
            True if session is active, False otherwise
        """
        return websocket_id in self.active_sessions

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_sessions)


# Global instance for singleton pattern
connection_manager = ConnectionManager()
