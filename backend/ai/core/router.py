"""
Provider Router: selects the best provider and handles fallback.
"""
from typing import Optional, List
from .config import AIConfig
from ..providers.base import AIRequest


class ProviderRouter:
    """Router for selecting AI providers with cost-optimized fallback."""

    PROVIDER_WEIGHTS = {
        'deepseek': 1.0,   # Primary - good quality/cost ratio
        'openai': 0.9,     # Backup - also good
        'claude': 0.8,     # Alternative
        'local': 0.3,      # Last resort (free but lower quality)
    }

    def __init__(self):
        self.available_providers = AIConfig.get_enabled_providers()
        self._failed_providers: set = set()

    def _is_simple_task(self, request: AIRequest) -> bool:
        """Determine if this is a simple task suitable for local AI."""
        return (
            request.max_tokens < 200
            and request.temperature < 0.5
            and len(request.prompt) < 500
        )

    def select_provider(self, request: AIRequest) -> str:
        """Select the best provider for a given request."""
        candidates = [
            p for p in self.available_providers
            if p not in self._failed_providers
        ]

        if not candidates:
            # All providers failed; reset and retry
            self._failed_providers.clear()
            candidates = list(self.available_providers)

        if not candidates:
            raise RuntimeError("No AI providers available. Check .env configuration.")

        # Cost optimization: simple tasks → local (free)
        if self._is_simple_task(request) and 'local' in candidates:
            return 'local'

        # Return best available by weight
        candidates.sort(key=lambda p: self.PROVIDER_WEIGHTS.get(p, 0), reverse=True)
        return candidates[0]

    def mark_failed(self, provider: str):
        """Mark a provider as failed (will be skipped on next selection)."""
        self._failed_providers.add(provider)

    def get_fallback(self, failed_provider: str) -> Optional[str]:
        """Get fallback provider when primary fails."""
        self.mark_failed(failed_provider)
        candidates = [
            p for p in self.available_providers
            if p not in self._failed_providers
        ]
        if not candidates:
            self._failed_providers.clear()
            candidates = [
                p for p in self.available_providers
                if p != failed_provider
            ]
        if not candidates:
            return None
        candidates.sort(key=lambda p: self.PROVIDER_WEIGHTS.get(p, 0), reverse=True)
        return candidates[0]
