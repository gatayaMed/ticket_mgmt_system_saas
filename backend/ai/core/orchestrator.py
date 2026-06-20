"""
AI Orchestrator: central controller that routes requests to the best provider
with caching, fallback, and metrics tracking.
"""
import time
import importlib
from typing import Dict, Optional
from .config import AIConfig
from .router import ProviderRouter
from .cache import AICacheManager
from ..providers.base import AIRequest, AIResponse, BaseAIProvider
from ..models import AIMetrics


class AIOrchestrator:
    """Central orchestrator for all AI requests."""

    # Lazy-loaded: provider_name → dotted path
    PROVIDER_MAP = {
        'deepseek': 'ai.providers.deepseek.DeepSeekProvider',
        'openai': 'ai.providers.openai.OpenAIProvider',
        'claude': 'ai.providers.claude.ClaudeProvider',
        'local': 'ai.providers.local.LocalAIProvider',
    }

    def __init__(self):
        self.router = ProviderRouter()
        self._provider_instances: Dict[str, BaseAIProvider] = {}

    def _get_provider(self, name: str) -> BaseAIProvider:
        """Get or create a provider instance (lazy import to avoid requiring all SDKs)."""
        if name not in self._provider_instances:
            config = AIConfig.get_provider_config(name)
            provider_path = self.PROVIDER_MAP.get(name)
            if not provider_path:
                raise ValueError(f"Unknown provider: {name}")
            module_path, class_name = provider_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)
            self._provider_instances[name] = provider_class(config)
        return self._provider_instances[name]

    def generate(self, request: AIRequest, use_cache: bool = True) -> AIResponse:
        """Generate a response with caching, routing, and fallback."""
        if use_cache:
            cached = AICacheManager.get(request)
            if cached:
                return cached

        provider_name = self.router.select_provider(request)
        response = self._try_generate(request, provider_name)

        if response and not response.error and use_cache:
            AICacheManager.set(request, response)

        return response

    async def generate_async(self, request: AIRequest, use_cache: bool = True) -> AIResponse:
        """Async version of generate."""
        if use_cache:
            cached = AICacheManager.get(request)
            if cached:
                return cached

        provider_name = self.router.select_provider(request)
        response = await self._try_generate_async(request, provider_name)

        if response and not response.error and use_cache:
            AICacheManager.set(request, response)

        return response

    def _try_generate(self, request: AIRequest, provider_name: str, attempt: int = 0) -> AIResponse:
        """Attempt generation with up to 2 fallback providers."""
        start = time.time()
        try:
            provider = self._get_provider(provider_name)
            response = provider.generate(request)
            AIMetrics.record(provider_name, 'generate', response.response_time,
                           tokens=response.usage.get('total_tokens', 0))
            return response
        except Exception as e:
            request_time = time.time() - start
            AIMetrics.record(provider_name, 'generate', request_time, success=False, error=str(e)[:500])

            if attempt >= 2:
                return AIResponse(
                    content='', model='', provider=provider_name,
                    usage={}, response_time=request_time, error=str(e)[:500]
                )

            fallback = self.router.get_fallback(provider_name)
            if fallback:
                return self._try_generate(request, fallback, attempt + 1)

            return AIResponse(
                content='', model='', provider=provider_name,
                usage={}, response_time=request_time, error=str(e)[:500]
            )

    async def _try_generate_async(self, request: AIRequest, provider_name: str, attempt: int = 0) -> AIResponse:
        """Async version of _try_generate."""
        start = time.time()
        try:
            provider = self._get_provider(provider_name)
            response = await provider.generate_async(request)
            AIMetrics.record(provider_name, 'generate', response.response_time,
                           tokens=response.usage.get('total_tokens', 0))
            return response
        except Exception as e:
            request_time = time.time() - start
            AIMetrics.record(provider_name, 'generate', request_time, success=False, error=str(e)[:500])

            if attempt >= 2:
                return AIResponse(
                    content='', model='', provider=provider_name,
                    usage={}, response_time=request_time, error=str(e)[:500]
                )

            fallback = self.router.get_fallback(provider_name)
            if fallback:
                return await self._try_generate_async(request, fallback, attempt + 1)

            return AIResponse(
                content='', model='', provider=provider_name,
                usage={}, response_time=request_time, error=str(e)[:500]
            )

    def classify_text(self, text: str, categories: list, provider_name: str = None) -> Dict[str, float]:
        """Classify text using the best available provider."""
        provider_name = provider_name or self.router.select_provider(
            AIRequest(prompt=text, max_tokens=100)
        )
        try:
            provider = self._get_provider(provider_name)
            return provider.classify(text, categories)
        except Exception:
            fallback = self.router.get_fallback(provider_name)
            if fallback:
                try:
                    return self._get_provider(fallback).classify(text, categories)
                except Exception:
                    pass
            return {cat: 0.0 for cat in categories}

    def embed(self, text: str, provider_name: str = None) -> list:
        """Generate embeddings using the best available provider."""
        provider_name = provider_name or self.router.select_provider(
            AIRequest(prompt=text, max_tokens=100)
        )
        try:
            return self._get_provider(provider_name).embed(text)
        except Exception:
            fallback = self.router.get_fallback(provider_name)
            if fallback:
                try:
                    return self._get_provider(fallback).embed(text)
                except Exception:
                    pass
            return []
