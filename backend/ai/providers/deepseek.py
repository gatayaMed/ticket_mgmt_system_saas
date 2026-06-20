"""
DeepSeek API provider implementation.
"""
import time
import json
import httpx
from typing import Dict, Any, List
from .base import BaseAIProvider, AIRequest, AIResponse


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek API provider."""

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://api.deepseek.com/v1')
        self.model = config.get('model', 'deepseek-chat')
        self.timeout = config.get('timeout', 30)

    @property
    def provider_name(self) -> str:
        return "deepseek"

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
        }

    def _parse_response(self, data: dict, request: AIRequest, start_time: float) -> AIResponse:
        choice = data.get('choices', [{}])[0]
        return AIResponse(
            content=choice.get('message', {}).get('content', ''),
            model=data.get('model', self.model),
            provider=self.provider_name,
            usage=data.get('usage', {}),
            response_time=round(time.time() - start_time, 3),
            raw_response=data,
        )

    def generate(self, request: AIRequest) -> AIResponse:
        start = time.time()
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = self._build_payload(request)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f'{self.base_url}/chat/completions',
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return self._parse_response(response.json(), request, start)

    async def generate_async(self, request: AIRequest) -> AIResponse:
        start = time.time()
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = self._build_payload(request)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}/chat/completions',
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return self._parse_response(response.json(), request, start)

    def classify(self, text: str, categories: List[str]) -> Dict[str, float]:
        prompt = f"""Classify the following text into one or more of these categories: {', '.join(categories)}.

Text: {text}

Return a JSON object with category names as keys and confidence scores (0.0 to 1.0) as values.
Only include categories that are relevant. Example: {{"bug": 0.9, "feature": 0.1}}"""

        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=200)
        response = self.generate(request)
        try:
            # Try to parse JSON from response
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            return {cat: 0.0 for cat in categories}

    def embed(self, text: str) -> List[float]:
        start = time.time()
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': self.model,
            'input': text,
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f'{self.base_url}/embeddings',
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get('data', [{}])[0].get('embedding', [])

    def health_check(self) -> bool:
        try:
            request = AIRequest(prompt="ping", max_tokens=5, temperature=0)
            self.generate(request)
            return True
        except Exception:
            return False
