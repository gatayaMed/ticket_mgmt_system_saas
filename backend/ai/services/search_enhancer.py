"""
Semantic search enhancer: improves search with AI understanding.
"""
from typing import Dict, Any, List
from django.db.models import Q
from tickets.models import Ticket
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest


class SearchEnhancer:
    """Enhance search queries with AI semantic understanding."""

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def enhance_query(self, query: str) -> Dict[str, Any]:
        """Expand a user's search query with synonyms and related terms."""
        prompt = (
            f"Given the search query: \"{query}\"\n"
            f"Return a JSON object with:\n"
            f"- 'enhanced_query': the original with relevant synonyms added\n"
            f"- 'keywords': list of 3-5 key search terms\n"
            f"- 'filters': suggested filters (status, priority, type)\n"
            f"Example: {{\"enhanced_query\": \"login bug error authentication\", "
            f"\"keywords\": [\"login\", \"authentication\", \"bug\"], "
            f"\"filters\": {{\"status\": \"any\", \"type\": \"bug\", \"priority\": \"high\"}}}}"
        )
        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=200)
        response = self.orchestrator.generate(request)

        try:
            import json
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            return json.loads(content)
        except Exception:
            return {'enhanced_query': query, 'keywords': query.split(), 'filters': {}}

    def search(self, query: str, user, limit: int = 20) -> List[Dict]:
        """Perform AI-enhanced ticket search."""
        from organizations.models import Organization

        enhanced = self.enhance_query(query)
        keywords = enhanced.get('keywords', [query])

        org_ids = Organization.objects.filter(
            memberships__user=user, memberships__is_active=True
        ).values_list('id', flat=True)

        # Build OR query for all keywords
        q_filter = Q()
        for kw in keywords[:5]:
            q_filter |= Q(title__icontains=kw) | Q(description__icontains=kw) | Q(ticket_id__icontains=kw)

        tickets = Ticket.objects.filter(
            project__organization_id__in=org_ids,
            is_active=True,
        ).filter(q_filter).select_related('project', 'assignee').distinct()[:limit]

        return [
            {
                'id': t.id, 'ticket_id': t.ticket_id, 'title': t.title,
                'status': t.status, 'priority': t.priority, 'ticket_type': t.ticket_type,
                'project': t.project.name, 'assignee': t.assignee.username if t.assignee else None,
                'updated_at': t.updated_at.isoformat(),
            }
            for t in tickets
        ]
