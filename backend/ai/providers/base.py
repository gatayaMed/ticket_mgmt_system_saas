"""
Abstract base provider and standardized request/response dataclasses.
All AI providers must inherit from BaseAIProvider.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class AIRequest:
    """Standardized AI request format across all providers."""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    context: Optional[Dict] = None
    model: Optional[str] = None


@dataclass
class AIResponse:
    """Standardized AI response format across all providers."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    response_time: float = 0.0
    raw_response: Optional[Dict] = None
    error: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for all AI providers."""

    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with configuration dictionary."""
        pass

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        """Generate AI response synchronously."""
        pass

    @abstractmethod
    async def generate_async(self, request: AIRequest) -> AIResponse:
        """Generate AI response asynchronously."""
        pass

    @abstractmethod
    def classify(self, text: str, categories: List[str]) -> Dict[str, float]:
        """Classify text into categories with confidence scores."""
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider is healthy."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name string."""
        pass
