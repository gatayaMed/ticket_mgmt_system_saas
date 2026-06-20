from django.conf import settings
from config.ai_settings import ai_settings


class AIConfig:
    """Centralized AI configuration accessor."""

    @staticmethod
    def is_provider_enabled(provider_name: str) -> bool:
        return ai_settings.get_provider_config(provider_name).get('enabled', False)

    @staticmethod
    def get_enabled_providers() -> list:
        return ai_settings.get_enabled_providers()

    @staticmethod
    def get_default_provider() -> str:
        enabled = ai_settings.get_enabled_providers()
        if not enabled:
            raise RuntimeError("No AI providers enabled. Check .env configuration.")
        return enabled[0]

    @staticmethod
    def get_provider_config(provider_name: str) -> dict:
        return ai_settings.get_provider_config(provider_name)

    @staticmethod
    def is_cache_enabled() -> bool:
        return ai_settings.AI_CACHE_ENABLED

    @staticmethod
    def get_cache_ttl() -> int:
        return ai_settings.AI_CACHE_TTL

    @staticmethod
    def is_auto_classify_enabled() -> bool:
        return ai_settings.AI_AUTO_CLASSIFY

    @staticmethod
    def get_max_suggestions() -> int:
        return ai_settings.AI_MAX_SUGGESTIONS

    @staticmethod
    def get_min_confidence() -> int:
        return ai_settings.AI_MIN_CONFIDENCE
