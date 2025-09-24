"""
WebSocket message handlers for pharmacy agent conversation.

This module extracts message handling logic to reduce complexity
and improve maintainability of the WebSocket endpoint.
"""

import logging
from typing import Dict, Optional
from src.agents.agent_factory import AgentFactory
from src.agents.base import ConversationalAgent
from src.agents.collection_agent import CollectionAgent
from src.websocket import connection_manager
from src.services.pharmacy_service import PharmacyService

logger = logging.getLogger(__name__)


async def handle_init_message(
    data: dict,
    session_id: str,
    pharmacy_service: PharmacyService,
    active_agents: Dict[str, ConversationalAgent],
) -> Optional[ConversationalAgent]:
    """
    Handle initialization message to create appropriate agent.

    Args:
        data: Message data containing phone number
        session_id: WebSocket session ID
        pharmacy_service: Pharmacy service instance
        active_agents: Dictionary of active agent sessions

    Returns:
        Created agent instance or None if error
    """
    phone = data.get("phone", "").strip()

    if not phone:
        success = await connection_manager.send_message(
            session_id,
            {
                "type": "error",
                "message": "Phone number is required to start the conversation.",
            },
        )
        if not success:
            logger.debug(f"Failed to send error message to {session_id}")
        return None

    try:
        # Create agent factory and appropriate agent
        factory = AgentFactory(pharmacy_service)
        agent = await factory.create_agent(phone, session_id)
        active_agents[session_id] = agent

        # Send agent ready message
        agent_type = agent.get_agent_type()

        if agent_type == "info":
            # Type narrowing: InfoAgent has pharmacy attribute
            from src.agents.info_agent import InfoAgent

            if isinstance(agent, InfoAgent):
                welcome_msg = (
                    f"Hello! I can help you with information about {agent.pharmacy.name}. "
                    "What would you like to know?"
                )
            else:
                welcome_msg = "Hello! I can help you with information. What would you like to know?"
        else:
            welcome_msg = (
                f"Hello! I see we don't have a pharmacy registered with the phone number {phone}. "
                "I'll help you register your pharmacy. Let's start with your pharmacy's name."
            )

        success = await connection_manager.send_message(
            session_id,
            {"type": "agent_ready", "agent_type": agent_type, "message": welcome_msg},
        )

        if not success:
            logger.warning(f"Failed to send agent ready message to {session_id}")
            # Clean up the agent if we couldn't send the ready message
            if session_id in active_agents:
                del active_agents[session_id]
            return None

        return agent

    except ValueError as e:
        await connection_manager.send_message(
            session_id, {"type": "error", "message": str(e)}
        )
        return None
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        await connection_manager.send_message(
            session_id,
            {
                "type": "error",
                "message": "Failed to initialize agent. Please try again.",
            },
        )
        return None


async def handle_regular_message(
    content: str, agent: ConversationalAgent, session_id: str
) -> None:
    """
    Process regular conversation message with agent.

    Args:
        content: Message content from user
        agent: Active agent instance
        session_id: WebSocket session ID
    """
    if not agent:
        success = await connection_manager.send_message(
            session_id,
            {
                "type": "error",
                "message": "Please initialize the conversation with a phone number first.",
            },
        )
        if not success:
            logger.debug(f"Failed to send initialization error to {session_id}")
        return

    try:
        response = await agent.process_message(content)

        # Build response data
        response_data = {"type": "response", "content": response}

        # Add collection progress if it's a collection agent
        if isinstance(agent, CollectionAgent):
            await handle_collection_progress(agent, response_data)

        success = await connection_manager.send_message(session_id, response_data)
        if not success:
            logger.warning(f"Failed to send response to {session_id}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await connection_manager.send_message(
            session_id,
            {"type": "error", "message": "Error processing message. Please try again."},
        )


async def handle_collection_progress(
    agent: CollectionAgent, response_data: dict
) -> None:
    """
    Add collection progress information to response.

    Args:
        agent: Collection agent instance
        response_data: Response data dictionary to update
    """
    status = agent.get_collection_status()

    if status["is_complete"]:
        pharmacy_data = agent.get_collected_pharmacy()
        response_data["type"] = "collection_complete"
        response_data["pharmacy_data"] = (
            pharmacy_data.model_dump() if pharmacy_data else None
        )
    else:
        response_data["type"] = "collection_progress"
        response_data["fields_collected"] = status["collected_fields"]
        response_data["fields_remaining"] = status["missing_fields"]


async def cleanup_agent_session(
    session_id: str, active_agents: Dict[str, ConversationalAgent]
) -> None:
    """
    Clean up agent session on disconnect.

    Args:
        session_id: WebSocket session ID
        active_agents: Dictionary of active agent sessions
    """
    # Disconnect from connection manager
    await connection_manager.disconnect(session_id)

    # Clean up agent if exists
    if session_id in active_agents:
        try:
            agent = active_agents[session_id]
            agent.clear_memory()
            del active_agents[session_id]
            logger.info(f"Cleaned up agent session: {session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up agent for {session_id}: {e}")

    logger.info(f"WebSocket session ended: {session_id}")
