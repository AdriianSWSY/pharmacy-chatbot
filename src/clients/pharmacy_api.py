"""
Client for interacting with the external pharmacy API.
"""

import asyncio
import logging
from typing import List
import httpx
from src.models.pharmacy import Pharmacy

logger = logging.getLogger(__name__)


class PharmacyAPIClient:
    """Handles communication with the external pharmacy API."""

    def __init__(
        self, base_url: str, timeout: int, retry_count: int, retry_delay: float
    ):
        """
        Initialize the pharmacy API client.

        Args:
            base_url: Base URL for the pharmacy API
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
            retry_delay: Initial delay between retries in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    async def fetch_pharmacies(self) -> List[Pharmacy]:
        """
        Fetch all pharmacies from the external API with retry logic.

        Returns:
            List of Pharmacy objects

        Raises:
            httpx.HTTPError: If the request fails after all retries
            ValueError: If the response data is invalid
        """
        last_error = None

        for attempt in range(self.retry_count):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(f"{self.base_url}/pharmacies")
                    response.raise_for_status()

                    # Parse and return pharmacy data
                    data = response.json()
                    return [Pharmacy(**item) for item in data]

            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code}")
                    raise

                # Log server errors and continue to retry
                last_error = e
                logger.warning(
                    f"Server error {e.response.status_code} on attempt {attempt + 1}"
                )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                # Network issues - worth retrying
                last_error = e
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")

            except ValueError as e:
                # JSON parsing error - don't retry
                logger.error(f"Invalid JSON response: {e}")
                raise

            # Wait before retrying (except on last attempt)
            if attempt < self.retry_count - 1:
                delay = self.retry_delay * (2**attempt)  # Exponential backoff
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

        # All retries failed - raise the last error
        logger.error(f"All {self.retry_count} attempts failed")
        if last_error:
            raise last_error
        raise httpx.RequestError("Failed to fetch pharmacies after all retries")
