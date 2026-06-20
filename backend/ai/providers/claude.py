"""
Anthropic Claude provider implementation.
"""
import time
from typing import Dict, Any, List
from .base import BaseAIProvider, AIRequest, AIResponse


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: Dict[str, Any]):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.get('api_key', ''))
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        self.model = config.get('model', 'claude-3-opus-20240229')

    @property
    def provider_name(self) -> str:
        return "claude"

    def generate(self, request: AIRequest) -> AIResponse:
        start = time.time()
        response = self.client.messages.create(
            model=request.model or self.model,
            max_tokens=request.max_tokens,
            system=request.system_prompt or "",
            messages=[{"role": "user", "content": request.prompt}],
        )
        usage = response.usage
        return AIResponse(
            content=response.content[0].text if response.content else '',
            model=response.model,
            provider=self.provider_name,
            usage={'input_tokens': usage.input_tokens, 'output_tokens': usage.output_tokens} if usage else {},
            response_time=round(time.time() - start, 3),
        )

    async def generate_async(self, request: AIRequest) -> AIResponse:
        import asyncio
        return await asyncio.to_thread(self.generate, request)

    def classify(self, text: str, categories: List[str]) -> Dict[str, float]:
        prompt = f"""Classify: "{text}" into: {', '.join(categories)}.
Return only a JSON object like {{"category": 0.9}}."""
        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=150)
        response = self.generate(request)
        try:
            import json
            content = response.content.strip().strip('```json').strip('```').strip()
            return json.loads(content)
        except Exception:
            return {cat: 0.0 for cat in categories}

    def embed(self, text: str) -> List[float]:
        # Claude does not have a dedicated embedding endpoint; return placeholder
        return []

    def health_check(self) -> bool:
        try:
            request = AIRequest(prompt="ping", max_tokens=5, temperature=0)
            self.generate(request)
            return True
        except Exception:
            return False
