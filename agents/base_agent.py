from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from google.api_core import exceptions as google_exceptions
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Define the global retry strategy for all agents
gemini_retry_strategy = retry(
    # Wait 4s, 8s, 16s... up to 60s between retries
    wait=wait_exponential(multiplier=1, min=4, max=60),
    # Stop trying after 5 failed attempts
    stop=stop_after_attempt(5),
    # Only retry if the error is "Resource Exhausted" (429)
    retry=retry_if_exception_type(google_exceptions.ResourceExhausted),
    reraise=True
)


class BaseAgent(ABC):
    """Shared interface for all agents."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform agent step and return updated state."""
        raise NotImplementedError
