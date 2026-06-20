"""
AI-powered sentiment analyzer: detects emotion in ticket text.
"""
from typing import Dict, Any
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest


class SentimentAnalyzer:
    """Analyze sentiment of ticket content and comments."""

    LABELS = ['positive', 'neutral', 'negative', 'frustrated', 'urgent']

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a text."""
        scores = self.orchestrator.classify_text(text, self.LABELS)
        if not scores:
            return {'sentiment': 'neutral', 'confidence': 0, 'scores': {}}

        best = max(scores, key=scores.get)
        return {
            'sentiment': best,
            'confidence': round(scores[best] * 100, 1),
            'scores': {k: round(v * 100, 1) for k, v in scores.items()},
        }

    def analyze_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Analyze sentiment for a specific ticket."""
        from tickets.models import Ticket, Comment
        ticket = Ticket.objects.get(id=ticket_id)
        text = f"Title: {ticket.title}\nDescription: {ticket.description}"

        comments = Comment.objects.filter(ticket=ticket, is_active=True)
        if comments.exists():
            text += "\nComments:\n" + "\n".join(c.content for c in comments[:10])

        return self.analyze(text)
