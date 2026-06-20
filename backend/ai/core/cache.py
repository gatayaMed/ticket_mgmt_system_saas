"""
Response caching for AI requests to reduce API calls and costs.
"""
import hashlib
import json
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import AICache
from ..providers.base import AIRequest, AIResponse
from .config import AIConfig


class AICacheManager:
    """Manages caching of AI responses to avoid redundant API calls."""

    @staticmethod
    def _make_cache_key(request: AIRequest) -> str:
        """Generate a deterministic cache key from the request."""
        raw = json.dumps({
            'p': request.prompt,
            's': request.system_prompt,
            't': request.temperature,
            'm': request.max_tokens,
            'model': request.model,
        }, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def get(request: AIRequest) -> AIResponse | None:
        """Retrieve a cached response if available and not expired."""
        if not AIConfig.is_cache_enabled():
            return None

        key = AICacheManager._make_cache_key(request)
        try:
            cached = AICache.objects.get(key=key)
            if cached.is_expired():
                cached.delete()
                return None
            data = cached.response
            return AIResponse(
                content=data['content'],
                model=data.get('model', ''),
                provider=data.get('provider', ''),
                usage=data.get('usage', {}),
                response_time=0.0,
            )
        except AICache.DoesNotExist:
            return None

    @staticmethod
    def set(request: AIRequest, response: AIResponse):
        """Store a response in the cache."""
        if not AIConfig.is_cache_enabled():
            return

        key = AICacheManager._make_cache_key(request)
        ttl = AIConfig.get_cache_ttl()
        expires_at = timezone.now() + timedelta(seconds=ttl)

        AICache.objects.update_or_create(
            key=key,
            defaults={
                'response': {
                    'content': response.content,
                    'model': response.model,
                    'provider': response.provider,
                    'usage': response.usage,
                },
                'provider': response.provider,
                'model': response.model,
                'expires_at': expires_at,
            }
        )

    @staticmethod
    def clear_expired():
        """Remove expired cache entries."""
        AICache.objects.filter(expires_at__lt=timezone.now()).delete()
