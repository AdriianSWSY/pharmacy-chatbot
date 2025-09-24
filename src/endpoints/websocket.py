"""
WebSocket endpoint for pharmacy agent conversation with improved error handling.
"""

import uuid
import json
import logging
from typing import Optional, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from src.websocket import connection_manager
from src.agents.base import ConversationalAgent
from src.dependencies import get_pharmacy_service
from src.endpoints.websocket_handlers import handle_init_message, handle_regular_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# Store active agent sessions
active_agents: Dict[str, ConversationalAgent] = {}


@router.websocket("/pharmacy-agent")
async def websocket_pharmacy_agent(
    websocket: WebSocket, pharmacy_service=Depends(get_pharmacy_service)
):
    """
    WebSocket endpoint for pharmacy agent conversation with improved error handling.

    Protocol:
    1. Client connects
    2. Client sends phone number as first message
    3. Server creates appropriate agent
    4. Bidirectional conversation flow
    """
    session_id = str(uuid.uuid4())
    agent: Optional[ConversationalAgent] = None
    connection_established = False

    try:
        await connection_manager.connect(session_id, websocket)
        connection_established = True

        await connection_manager.send_message(
            session_id,
            {
                "type": "connection_established",
                "session_id": session_id,
                "message": "Connection established. Please provide a phone number to start.",
            },
        )

        # Main conversation loop
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type", "message")
                content = data.get("content", "")

                if message_type == "close":
                    logger.info(f"Client requested close for session: {session_id}")
                    break
                elif message_type == "init":
                    agent = await handle_init_message(
                        data, session_id, pharmacy_service, active_agents
                    )
                elif message_type == "message":
                    logger.debug(f"Processing message for session {session_id}")
                    await handle_regular_message(content, agent, session_id)

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {session_id}")
                break
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON from {session_id}: {e}")
                # Check if still connected before sending error
                if connection_manager.is_connected(session_id):
                    await connection_manager.send_message(
                        session_id,
                        {
                            "type": "error",
                            "message": "Invalid message format. Please send valid JSON.",
                        },
                    )
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                # Check if still connected before sending error
                if connection_manager.is_connected(session_id):
                    await connection_manager.send_message(
                        session_id,
                        {"type": "error", "message": "An unexpected error occurred."},
                    )
                else:
                    break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during setup: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Clean up with better error handling
        if connection_established:
            # Check if still in active connections before cleanup
            if connection_manager.is_connected(session_id):
                await connection_manager.disconnect(session_id)

            # Clean up agent session
            if session_id in active_agents:
                try:
                    agent = active_agents[session_id]
                    agent.clear_memory()
                    del active_agents[session_id]
                    logger.info(f"Cleaned up agent session: {session_id}")
                except Exception as e:
                    logger.error(f"Error cleaning up agent session {session_id}: {e}")

        logger.info(f"WebSocket session fully closed: {session_id}")
