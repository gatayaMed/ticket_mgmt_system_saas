"""
AI Chatbot: natural language assistant for the ticket system.
"""
import json
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest

User = get_user_model()


class TicketChatbot:
    """AI chatbot for ticket management assistance."""

    SYSTEM_PROMPT = """You are TicketBot, an AI assistant for a ticket management system.
You help users create, find, and manage tickets. You can:
- Create tickets (collect title, description, project)
- Look up ticket status
- Search for tickets
- Suggest who to assign tickets to
- Answer questions about the system
Be concise, friendly, and helpful. Format actions when suggesting ticket creation."""

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def chat(self, message: str, user_id: int, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle a chat message and return AI response with optional actions."""
        user = User.objects.get(id=user_id)

        context_info = self._build_context(user, context)
        prompt = (
            f"User: {message}\n\n"
            f"Context: {context_info}\n\n"
            f"Respond helpfully. If the user wants to create a ticket, "
            f"suggest collecting a title and description. "
            f"If searching, help refine the query."
        )

        request = AIRequest(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=500,
        )

        response = self.orchestrator.generate(request)
        actions = self._extract_actions(response.content)

        return {
            'response': response.content,
            'actions': actions,
            'model': response.model,
            'provider': response.provider,
        }

    def chat_sync(self, message: str, user_id: int) -> Dict[str, Any]:
        """Synchronous wrapper for chat."""
        return self.chat(message, user_id)

    def _build_context(self, user: User, extra_context: Optional[Dict]) -> str:
        """Build context information for the AI."""
        parts = []

        # Recent tickets
        recent = Ticket.objects.filter(
            assignee=user, is_active=True
        ).order_by('-created_at')[:5]
        if recent:
            parts.append("User's recent tickets:\n" + "\n".join(
                f"- {t.ticket_id}: {t.title} ({t.get_status_display()})"
                for t in recent
            ))

        if extra_context:
            parts.append(f"Additional context: {json.dumps(extra_context)}")

        return "\n".join(parts) if parts else "No additional context"

    def _extract_actions(self, response: str) -> list:
        """Extract structured actions from AI response."""
        actions = []
        lower = response.lower()

        if any(phrase in lower for phrase in ['create ticket', 'create a ticket', 'new ticket']):
            actions.append({'type': 'create_ticket', 'suggested': True})

        if any(phrase in lower for phrase in ['search', 'find ticket']):
            actions.append({'type': 'search', 'suggested': True})

        if 'assign' in lower:
            actions.append({'type': 'suggest_assignee', 'suggested': True})

        return actions
