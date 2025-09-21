"""
Client for interacting with the external pharmacy API.
"""

import asyncio
import logging
import random
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.retry_count):
                try:
                    response = await client.get(f"{self.base_url}/pharmacies")
                    response.raise_for_status()

                    # Parse response data into Pharmacy models
                    data = response.json()
                    return [Pharmacy(**item) for item in data]

                except httpx.TimeoutException as e:
                    logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")

                except httpx.NetworkError as e:
                    logger.warning(f"Network error on attempt {attempt + 1}: {e}")

                except httpx.HTTPStatusError as e:
                    logger.warning(
                        f"HTTP {e.response.status_code} on attempt {attempt + 1}: {e.response.text[:200]}"
                    )
                    # Don't retry on 4xx errors (client errors)
                    if 400 <= e.response.status_code < 500:
                        logger.error(
                            f"Client error {e.response.status_code}, not retrying"
                        )
                        raise

                except ValueError as e:
                    logger.error(f"Invalid JSON response on attempt {attempt + 1}: {e}")
                    # JSON parsing errors shouldn't be retried
                    raise

                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt == self.retry_count - 1:
                        raise

                # Apply retry logic for retryable errors
                if attempt < self.retry_count - 1:
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2**attempt) + (random.random() * 0.1)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)

            logger.error(f"All {self.retry_count} attempts failed")
            return []
