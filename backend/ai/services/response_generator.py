"""
AI-powered response generator: drafts responses for tickets.
"""
from typing import Dict, Any
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest


class ResponseGenerator:
    """Generate draft responses for tickets."""

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def generate(self, ticket_id: int) -> Dict[str, Any]:
        """Generate a draft response for a ticket."""
        from tickets.models import Ticket, Comment
        try:
            ticket = Ticket.objects.select_related('project').get(id=ticket_id, is_active=True)
        except Ticket.DoesNotExist:
            return {'error': 'Ticket not found'}

        # Build context from recent comments
        comments = Comment.objects.filter(ticket=ticket, is_active=True).order_by('-created_at')[:5]
        comment_text = "\n".join(f"- {c.user.username}: {c.content}" for c in comments)

        prompt = (
            f"You are a helpful support agent drafting a response for a ticket.\n\n"
            f"Ticket: {ticket.ticket_id} - {ticket.title}\n"
            f"Status: {ticket.get_status_display()}\n"
            f"Priority: {ticket.get_priority_display()}\n"
            f"Description: {ticket.description[:500]}\n\n"
        )
        if comment_text:
            prompt += f"Recent comments:\n{comment_text}\n\n"

        prompt += (
            "Write a professional, helpful draft response. "
            "If the issue is resolved, include a closing note. "
            "If more info is needed, ask clear questions."
        )

        request = AIRequest(prompt=prompt, temperature=0.5, max_tokens=400)
        response = self.orchestrator.generate(request)

        return {
            'ticket_id': ticket.id,
            'ticket_code': ticket.ticket_id,
            'draft_response': response.content,
            'model': response.model,
            'provider': response.provider,
        }
