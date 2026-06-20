"""
Local AI provider using Ollama (or compatible OpenAI-compatible endpoint).
"""
import time
import json
import httpx
from typing import Dict, Any, List
from .base import BaseAIProvider, AIRequest, AIResponse


class LocalAIProvider(BaseAIProvider):
    """Local AI provider via Ollama or any OpenAI-compatible endpoint."""

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama2')
        self.timeout = config.get('timeout', 60)  # Local models can be slower

    @property
    def provider_name(self) -> str:
        return "local"

    def _build_payload(self, request: AIRequest) -> dict:
        messages = []
        if request.system_prompt:
            messages.append({'role': 'system', 'content': request.system_prompt})
        messages.append({'role': 'user', 'content': request.prompt})
        return {
            'model': request.model or self.model,
            'messages': messages,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'stream': False,
        }

    def _call_ollama(self, payload: dict) -> dict:
        """Call Ollama chat API."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f'{self.base_url}/api/chat',
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def _call_ollama_async(self, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}/api/chat',
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def generate(self, request: AIRequest) -> AIResponse:
        start = time.time()
        payload = self._build_payload(request)
        data = self._call_ollama(payload)
        return AIResponse(
            content=data.get('message', {}).get('content', ''),
            model=data.get('model', self.model),
            provider=self.provider_name,
            usage=data.get('usage', {}),
            response_time=round(time.time() - start, 3),
        )

    async def generate_async(self, request: AIRequest) -> AIResponse:
        start = time.time()
        payload = self._build_payload(request)
        data = await self._call_ollama_async(payload)
        return AIResponse(
            content=data.get('message', {}).get('content', ''),
            model=data.get('model', self.model),
            provider=self.provider_name,
            usage=data.get('usage', {}),
            response_time=round(time.time() - start, 3),
        )

    def classify(self, text: str, categories: List[str]) -> Dict[str, float]:
        prompt = f"""Classify: "{text}" into: {', '.join(categories)}.
Return only a JSON object like {{"category": 0.9}}."""
        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=150)
        response = self.generate(request)
        try:
            content = response.content.strip().strip('```json').strip('```').strip()
            return json.loads(content)
        except Exception:
            return {cat: 0.0 for cat in categories}

    def embed(self, text: str) -> List[float]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f'{self.base_url}/api/embeddings',
                    json={'model': self.model, 'prompt': text}
                )
                response.raise_for_status()
                return response.json().get('embedding', [])
        except Exception:
            return []

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f'{self.base_url}/api/tags')
                return resp.status_code == 200
        except Exception:
            return False
