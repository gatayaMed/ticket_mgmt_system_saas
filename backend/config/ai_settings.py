"""
AI-specific settings loaded from environment variables.
All AI configuration lives here for clean separation from main settings.
"""
import os
from decouple import config as env_config, Csv


class AISettings:
    """Singleton to hold AI configuration."""

    # ============ PROVIDER ENABLED FLAGS ============
    DEEPSEEK_ENABLED = env_config('DEEPSEEK_ENABLED', default=True, cast=bool)
    OPENAI_ENABLED = env_config('OPENAI_ENABLED', default=False, cast=bool)
    CLAUDE_ENABLED = env_config('CLAUDE_ENABLED', default=False, cast=bool)
    LOCAL_AI_ENABLED = env_config('LOCAL_AI_ENABLED', default=False, cast=bool)

    # ============ DEEPSEEK ============
    DEEPSEEK_API_KEY = env_config('DEEPSEEK_API_KEY', default='')
    DEEPSEEK_BASE_URL = env_config('DEEPSEEK_BASE_URL', default='https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = env_config('DEEPSEEK_MODEL', default='deepseek-chat')
    DEEPSEEK_TIMEOUT = env_config('DEEPSEEK_TIMEOUT', default=30, cast=int)

    # ============ OPENAI ============
    OPENAI_API_KEY = env_config('OPENAI_API_KEY', default='')
    OPENAI_MODEL = env_config('OPENAI_MODEL', default='gpt-4-turbo-preview')

    # ============ CLAUDE ============
    CLAUDE_API_KEY = env_config('CLAUDE_API_KEY', default='')
    CLAUDE_MODEL = env_config('CLAUDE_MODEL', default='claude-3-opus-20240229')

    # ============ LOCAL AI (OLLAMA) ============
    LOCAL_AI_URL = env_config('LOCAL_AI_URL', default='http://localhost:11434')
    LOCAL_AI_MODEL = env_config('LOCAL_AI_MODEL', default='llama2')

    # ============ CACHE ============
    AI_CACHE_ENABLED = env_config('AI_CACHE_ENABLED', default=True, cast=bool)
    AI_CACHE_TTL = env_config('AI_CACHE_TTL', default=3600, cast=int)

    # ============ RATE LIMITING ============
    AI_RATE_LIMIT_ENABLED = env_config('AI_RATE_LIMIT_ENABLED', default=True, cast=bool)
    AI_RATE_LIMIT_REQUESTS = env_config('AI_RATE_LIMIT_REQUESTS', default=100, cast=int)
    AI_RATE_LIMIT_PERIOD = env_config('AI_RATE_LIMIT_PERIOD', default=60, cast=int)

    # ============ ASSIGNMENT ============
    AI_AUTO_CLASSIFY = env_config('AI_AUTO_CLASSIFY', default=True, cast=bool)
    AI_AUTO_PRIORITY = env_config('AI_AUTO_PRIORITY', default=True, cast=bool)
    AI_MAX_SUGGESTIONS = env_config('AI_MAX_SUGGESTIONS', default=5, cast=int)
    AI_MIN_CONFIDENCE = env_config('AI_MIN_CONFIDENCE', default=50, cast=int)

    @classmethod
    def get_provider_config(cls, provider_name: str) -> dict:
        """Get config dict for a specific provider."""
        provider_name = provider_name.upper()
        return {
            'enabled': getattr(cls, f'{provider_name}_ENABLED', False),
            'api_key': getattr(cls, f'{provider_name}_API_KEY', ''),
            'base_url': getattr(cls, f'{provider_name}_BASE_URL', None),
            'model': getattr(cls, f'{provider_name}_MODEL', None),
            'timeout': getattr(cls, f'{provider_name}_TIMEOUT', 30),
        }

    @classmethod
    def get_enabled_providers(cls) -> list:
        """Return list of enabled provider names."""
        providers = []
        for name in ['deepseek', 'openai', 'claude', 'local']:
            if getattr(cls, f'{name.upper()}_ENABLED', False):
                providers.append(name)
        return providers


# Singleton instance for import
ai_settings = AISettings()
