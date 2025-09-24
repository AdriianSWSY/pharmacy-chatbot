"""
Information agent for handling queries about existing pharmacy companies.
"""

import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from src.agents.base import ConversationalAgent
from src.agents.memory import agent_memory
from src.agents.tools.pharmacy_tools import create_pharmacy_tools
from src.models.pharmacy import Pharmacy
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class InfoAgent(ConversationalAgent):
    """Handles queries about existing pharmacy companies."""

    def __init__(self, session_id: str, pharmacy: Pharmacy):
        """
        Initialize the information agent.

        Args:
            session_id: Unique session identifier
            pharmacy: Pharmacy instance with data
        """
        # Get memory from the global agent memory manager
        memory = agent_memory.get_or_create_memory(session_id)
        super().__init__(session_id, memory)

        self.pharmacy = pharmacy
        self.settings = get_settings()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.agent.model,
            temperature=self.settings.agent.temperature,
            max_tokens=self.settings.agent.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Create tools
        self.tools = create_pharmacy_tools(pharmacy)

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=f"""You are a helpful pharmacy assistant. You have access to information about {pharmacy.name}.
Available details: name, phone, email, city, state, and prescriptions.
Be helpful and answer questions about this pharmacy company.
Use the tools available to query specific information when needed."""
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agent
        self.agent = create_tool_calling_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )

        # Create executor with memory
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,  # Pass memory to the executor
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
        )

        logger.info(f"Initialized InfoAgent for pharmacy: {pharmacy.name}")

    async def process_message(self, message: str) -> str:
        """
        Process an incoming message and return a response.

        Args:
            message: The user's message

        Returns:
            The agent's response
        """
        try:
            # Invoke the agent executor
            response = await self.executor.ainvoke({"input": message})

            # Extract the output
            output = response.get("output", "I couldn't process that request.")

            logger.info(f"InfoAgent processed message for session {self.session_id}")
            return output

        except Exception as e:
            logger.error(f"Error processing message in InfoAgent: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def get_agent_type(self) -> str:
        """
        Get the type of agent.

        Returns:
            String identifying the agent type
        """
        return "info"

    def get_pharmacy_info(self) -> dict:
        """
        Get basic pharmacy information.

        Returns:
            Dictionary with pharmacy details
        """
        return {
            "id": self.pharmacy.id,
            "name": self.pharmacy.name,
            "phone": self.pharmacy.phone,
            "email": self.pharmacy.email,
            "city": self.pharmacy.city,
            "state": self.pharmacy.state,
            "prescription_count": len(self.pharmacy.prescriptions)
            if self.pharmacy.prescriptions
            else 0,
        }
