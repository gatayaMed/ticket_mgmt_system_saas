"""
OpenAI GPT provider implementation.
"""
import time
from typing import Dict, Any, List
from .base import BaseAIProvider, AIRequest, AIResponse


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider."""

    def __init__(self, config: Dict[str, Any]):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.get('api_key', ''))
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        self.model = config.get('model', 'gpt-4-turbo-preview')

    @property
    def provider_name(self) -> str:
        return "openai"

    def _build_messages(self, request: AIRequest) -> list:
        messages = []
        if request.system_prompt:
            messages.append({'role': 'system', 'content': request.system_prompt})
        messages.append({'role': 'user', 'content': request.prompt})
        return messages

    def generate(self, request: AIRequest) -> AIResponse:
        start = time.time()
        response = self.client.chat.completions.create(
            model=request.model or self.model,
            messages=self._build_messages(request),
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        choice = response.choices[0]
        usage = response.usage
        return AIResponse(
            content=choice.message.content or '',
            model=response.model,
            provider=self.provider_name,
            usage={'prompt_tokens': usage.prompt_tokens, 'completion_tokens': usage.completion_tokens, 'total_tokens': usage.total_tokens} if usage else {},
            response_time=round(time.time() - start, 3),
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
        )

    async def generate_async(self, request: AIRequest) -> AIResponse:
        # OpenAI SDK doesn't have native async; wrap sync call
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
        resp = self.client.embeddings.create(model='text-embedding-3-small', input=text)
        return resp.data[0].embedding

    def health_check(self) -> bool:
        try:
            request = AIRequest(prompt="ping", max_tokens=5, temperature=0)
            self.generate(request)
            return True
        except Exception:
            return False
