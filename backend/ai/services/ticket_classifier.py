"""
AI-powered ticket classifier: auto-categorizes tickets by type.
"""
from typing import Dict, Any
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest


class TicketClassifier:
    """Classify tickets by type (bug, feature, task, improvement, epic)."""

    CATEGORIES = ['bug', 'feature', 'task', 'improvement', 'epic']

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def classify(self, title: str, description: str) -> Dict[str, Any]:
        """Classify a ticket and return category + confidence."""
        text = f"Title: {title}\nDescription: {description}"
        scores = self.orchestrator.classify_text(text, self.CATEGORIES)

        if not scores:
            return {'category': 'task', 'confidence': 0.0, 'scores': {}}

        best = max(scores, key=scores.get)
        return {
            'category': best,
            'confidence': round(scores[best] * 100, 1),
            'scores': {k: round(v * 100, 1) for k, v in scores.items()},
        }

    def classify_sync(self, title: str, description: str) -> Dict[str, Any]:
        """Synchronous wrapper for classify."""
        return self.classify(title, description)
