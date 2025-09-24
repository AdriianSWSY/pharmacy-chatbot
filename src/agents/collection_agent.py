"""
Collection agent for gathering new pharmacy information through conversation.
"""

import os
import re
from typing import Optional, Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.agents.base import ConversationalAgent
from src.agents.memory import agent_memory
from src.models.pharmacy import Pharmacy, Prescription
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class CollectionAgent(ConversationalAgent):
    """Collects new pharmacy information through conversation."""

    REQUIRED_FIELDS = ["name", "email", "city", "state"]
    OPTIONAL_FIELDS = ["prescriptions"]

    def __init__(self, session_id: str, phone: str):
        """
        Initialize the collection agent.

        Args:
            session_id: Unique session identifier
            phone: Phone number (already collected)
        """
        # Get memory from the global agent memory manager
        memory = agent_memory.get_or_create_memory(session_id)
        super().__init__(session_id, memory)

        self.phone = phone
        self.collected_data: Dict[str, Any] = {"phone": phone}
        self.settings = get_settings()
        self.validation_errors: Dict[str, str] = {}

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.agent.model,
            temperature=self.settings.agent.temperature,
            max_tokens=self.settings.agent.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Create prompt template for collection
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a friendly pharmacy registration assistant.
Your task is to naturally collect the following information:
- Company name (required)
- Email address (required)
- City (required)
- State (required)
- Prescription information (optional - can be multiple)

Guide the conversation naturally. Ask for one or two pieces of information at a time.
If the user provides multiple pieces of information, acknowledge all of them.
Be friendly and professional. If they don't have prescription information yet, that's okay.
Remember what the user has already told you and don't ask for the same information twice.""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # Create LLM chain
        self.chain = LLMChain(
            llm=self.llm, prompt=self.prompt, memory=self.memory, verbose=True
        )

        # Create extraction prompt for parsing user responses
        extraction_system_msg = """You are an information extraction assistant. Extract pharmacy company information from the user's message.

Your task is to extract the following information if present:
- name: company/pharmacy name
- email: email address
- city: city name from any location mention
- state: state name or abbreviation (CA, California, NY, New York, MA, Massachusetts, etc.)
- prescriptions: list of prescription/medication names

Location parsing rules:
- "San Francisco, California" extracts both city: San Francisco and state: California
- "Boston, MA" extracts both city: Boston and state: MA
- "located in Boston, MA" extracts both city: Boston and state: MA
- "We're in Boston" extracts city: Boston

Examples of valid JSON outputs:
- For "Our pharmacy is MedPlus Pharmacy": {{"name": "MedPlus Pharmacy"}}
- For "We're located in Boston, MA": {{"city": "Boston", "state": "MA"}}
- For "Our email is info@medplus.com": {{"email": "info@medplus.com"}}
- For "We have Lisinopril and Metformin": {{"prescriptions": ["Lisinopril", "Metformin"]}}

CRITICAL: You MUST respond with ONLY a valid JSON object, nothing else. No explanations, no text before or after.
If nothing is found, respond with: {{}}"""

        self.extraction_prompt = ChatPromptTemplate.from_messages(
            [("system", extraction_system_msg), ("human", "{input}")]
        )

        self.extraction_chain = LLMChain(
            llm=self.llm, prompt=self.extraction_prompt, verbose=False
        )

        logger.info(f"Initialized CollectionAgent with phone: {phone}")

    async def process_message(self, message: str) -> str:
        """
        Process an incoming message and return a response.

        Args:
            message: The user's message

        Returns:
            The agent's response
        """
        try:
            # First, try to extract information from the message
            extracted = await self._extract_information(message)
            print(f"DEBUG: Extracted data: {extracted}")
            logger.info(f"Extracted data: {extracted}")
            if extracted:
                self._update_collected_data(extracted)
                print(f"DEBUG: After update - collected_data: {self.collected_data}")
                logger.info(f"After update - collected_data: {self.collected_data}")

            # Generate response based on what's been collected
            missing_fields = self._get_missing_fields()
            collected_fields = [k for k in self.collected_data.keys() if k != "phone"]

            # Create enhanced message with context
            context_info = f"\n[Context: Collected: {', '.join(collected_fields) if collected_fields else 'none yet'}. Still need: {', '.join(missing_fields) if missing_fields else 'all required fields collected'}]"
            enhanced_message = message + context_info

            # Get response from LLM - only pass input
            response = await self.chain.arun(input=enhanced_message)

            # If all required fields are collected, add a completion message
            if self.is_complete():
                response += "\n\nGreat! I have all the required information. The pharmacy registration is complete."

            logger.info(
                f"CollectionAgent processed message for session {self.session_id}"
            )
            return response

        except Exception as e:
            logger.error(f"Error processing message in CollectionAgent: {e}")
            return (
                "I apologize, but I encountered an error. Could you please repeat that?"
            )

    async def _extract_information(self, message: str) -> Dict[str, Any]:
        """
        Extract pharmacy information from user message.

        Args:
            message: User's message

        Returns:
            Dictionary of extracted information
        """
        try:
            # Use LLM to extract structured data
            extraction_result = await self.extraction_chain.arun(input=message)
            print("Result in extraction: ", extraction_result)

            # Clean up the response - sometimes LLMs add extra text
            extraction_result = extraction_result.strip()

            # Try to extract JSON even if there's extra text
            import json
            import re

            # First try direct parsing
            try:
                extracted = json.loads(extraction_result)
            except json.JSONDecodeError:
                # Try to find JSON object in the text
                json_match = re.search(r"\{[^{}]*\}", extraction_result)
                if json_match:
                    try:
                        extracted = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Failed to parse extraction result as JSON: {extraction_result}"
                        )
                        return {}
                else:
                    logger.warning(
                        f"No JSON found in extraction result: {extraction_result}"
                    )
                    return {}

            # Validate extracted data
            validated = {}

            if "name" in extracted and extracted["name"]:
                validated["name"] = extracted["name"]

            if "email" in extracted and extracted["email"]:
                if self._validate_email(extracted["email"]):
                    validated["email"] = extracted["email"]

            if "city" in extracted and extracted["city"]:
                validated["city"] = extracted["city"]

            if "state" in extracted and extracted["state"]:
                validated["state"] = extracted["state"]

            if "prescriptions" in extracted and extracted["prescriptions"]:
                if isinstance(extracted["prescriptions"], list):
                    validated["prescriptions"] = extracted["prescriptions"]
                elif isinstance(extracted["prescriptions"], str):
                    validated["prescriptions"] = [extracted["prescriptions"]]

            logger.info(f"Successfully extracted and validated: {validated}")
            return validated

        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return {}

    def _update_collected_data(self, data: Dict[str, Any]):
        """
        Update collected data with new information.

        Args:
            data: Dictionary of new data
        """
        for key, value in data.items():
            if key == "prescriptions":
                # Append prescriptions to existing list
                if "prescriptions" not in self.collected_data:
                    self.collected_data["prescriptions"] = []
                if isinstance(value, list):
                    self.collected_data["prescriptions"].extend(value)
                else:
                    self.collected_data["prescriptions"].append(value)
            else:
                self.collected_data[key] = value

        logger.info(f"Updated collected data: {list(self.collected_data.keys())}")

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _get_missing_fields(self) -> List[str]:
        """
        Get list of missing required fields.

        Returns:
            List of field names that are still missing
        """
        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in self.collected_data:
                missing.append(field)
        return missing

    def is_complete(self) -> bool:
        """
        Check if all required fields have been collected.

        Returns:
            True if all required fields are collected, False otherwise
        """
        return len(self._get_missing_fields()) == 0

    def get_collected_pharmacy(self) -> Optional[Pharmacy]:
        """
        Get the collected pharmacy data as a Pharmacy object.

        Returns:
            Pharmacy object if complete, None otherwise
        """
        if not self.is_complete():
            return None

        # Create prescriptions list
        prescriptions = []
        if "prescriptions" in self.collected_data:
            for idx, prescription_name in enumerate(
                self.collected_data["prescriptions"]
            ):
                prescriptions.append(
                    Prescription(
                        drug=prescription_name,
                        count=0,  # Default value for now
                    )
                )

        # Create and return Pharmacy object
        return Pharmacy(
            id=0,  # Will be assigned by the system
            name=self.collected_data["name"],
            phone=self.collected_data["phone"],
            email=self.collected_data["email"],
            city=self.collected_data["city"],
            state=self.collected_data["state"],
            prescriptions=prescriptions,
        )

    def get_agent_type(self) -> str:
        """
        Get the type of agent.

        Returns:
            String identifying the agent type
        """
        return "collection"

    def get_collection_status(self) -> dict:
        """
        Get the current collection status.

        Returns:
            Dictionary with collection status details
        """
        return {
            "collected_fields": list(self.collected_data.keys()),
            "missing_fields": self._get_missing_fields(),
            "is_complete": self.is_complete(),
            "validation_errors": self.validation_errors,
        }
