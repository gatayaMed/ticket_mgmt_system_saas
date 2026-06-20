"""
AI-powered similar ticket finder: detects duplicate/similar tickets.
"""
from typing import Dict, Any, List
from django.db.models import Q
from tickets.models import Ticket
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest


class SimilarTicketFinder:
    """Find tickets similar to a given ticket."""

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def find(self, ticket_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find tickets similar to the given ticket."""
        try:
            source = Ticket.objects.select_related('project').get(id=ticket_id)
        except Ticket.DoesNotExist:
            return []

        # First, do a text-based search for candidates
        candidates = Ticket.objects.filter(
            project=source.project,
            is_active=True
        ).exclude(id=source.id).values('id', 'title', 'description', 'ticket_id')[:20]

        if not candidates:
            return []

        # Use AI to rank similarity
        candidate_texts = "\n---\n".join(
            f"ID:{c['id']} | {c['title']} | {c['description'][:200]}"
            for c in candidates
        )

        prompt = (
            f"Source ticket:\nTitle: {source.title}\nDescription: {source.description[:500]}\n\n"
            f"Candidate tickets:\n{candidate_texts}\n\n"
            f"Return a JSON array of the top {limit} most similar ticket IDs ranked by relevance. "
            f"Format: [{{\"id\": 1, \"score\": 0.95, \"reason\": \"...\"}}]"
        )

        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=300)
        response = self.orchestrator.generate(request)

        try:
            import json
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            results = json.loads(content)
            return results[:limit]
        except Exception:
            # Fallback: return top candidates by title similarity
            return [
                {'id': c['id'], 'score': 0.5, 'reason': 'Title match'}
                for c in candidates[:limit]
            ]

    def find_sync(self, ticket: object) -> list:
        """Synchronous wrapper accepting a Ticket instance."""
        return self.find(ticket.id)
