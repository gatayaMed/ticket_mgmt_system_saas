"""
AI-powered assignee suggester with manager approval workflow.
"""
import json
from typing import Dict, Any, List
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from ..core.orchestrator import AIOrchestrator
from ..providers.base import AIRequest
from ..models import DeveloperProfile, AssignmentHistory, AIAssignmentSuggestion

User = get_user_model()


class AssigneeSuggester:
    """AI-powered assignee suggestion with manager approval workflow."""

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    def get_suggestions(self, ticket_id: int) -> Dict[str, Any]:
        """Get AI suggestions for a ticket."""
        try:
            ticket = Ticket.objects.select_related('project').get(id=ticket_id, is_active=True)
        except Ticket.DoesNotExist:
            return {'error': 'Ticket not found'}

        # Check if pending suggestion exists
        existing = AIAssignmentSuggestion.objects.filter(
            ticket=ticket, status='pending'
        ).first()
        if existing:
            return {
                'suggestions': existing.suggestions,
                'criteria_used': existing.criteria_used,
                'suggestion_id': existing.id,
                'is_pending': True,
                'status': existing.status,
            }

        # Get project members (potential assignees)
        from projects.models import ProjectMember
        members = ProjectMember.objects.filter(
            project=ticket.project, is_active=True
        ).select_related('user')

        if not members:
            return {'suggestions': [], 'reason': 'No project members available'}

        # Build context for AI
        member_data = []
        for m in members:
            profile = DeveloperProfile.objects.filter(user=m.user).first()
            workload = Ticket.objects.filter(
                assignee=m.user, is_active=True
            ).exclude(status__in=['done', 'closed']).count()

            member_data.append({
                'user_id': m.user.id,
                'username': m.user.username,
                'skills': profile.skills if profile else {},
                'current_workload': workload,
                'tickets_completed': profile.tickets_completed if profile else 0,
                'success_rate': round(profile.success_rate or 0, 1),
            })

        prompt = (
            f"Ticket: {ticket.title}\nDescription: {ticket.description[:500]}\n\n"
            f"Available developers:\n{json.dumps(member_data, indent=2)}\n\n"
            f"Based on skills, current workload, and past performance, rank the top developers "
            f"for this ticket. For each suggestion provide: user_id, score (0-100), and reasoning.\n"
            f"Return a JSON array: [{{\"user_id\": 1, \"score\": 85, \"reasoning\": \"...\"}}]"
        )

        request = AIRequest(prompt=prompt, temperature=0.3, max_tokens=500)
        response = self.orchestrator.generate(request)

        try:
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            suggestions = json.loads(content)
        except Exception:
            # Fallback: simple workload-based ranking
            suggestions = sorted(member_data, key=lambda m: m['current_workload'])
            suggestions = [
                {'user_id': m['user_id'], 'score': max(100 - m['current_workload'] * 15, 10),
                 'reasoning': f"Low workload ({m['current_workload']} tickets)"}
                for m in suggestions[:5]
            ]

        # Save suggestion for manager approval
        ai_suggestion = AIAssignmentSuggestion.objects.create(
            ticket=ticket,
            suggestions=suggestions,
            criteria_used={'ticket_type': ticket.ticket_type, 'priority': ticket.priority},
            status='pending',
        )

        return {
            'suggestions': suggestions,
            'criteria_used': ai_suggestion.criteria_used,
            'suggestion_id': ai_suggestion.id,
            'is_pending': True,
            'status': 'pending',
        }

    def approve(self, suggestion_id: int, user_id: int, manager: User, notes: str = '') -> Dict:
        """Manager approves an AI suggestion."""
        try:
            suggestion = AIAssignmentSuggestion.objects.get(id=suggestion_id)
        except AIAssignmentSuggestion.DoesNotExist:
            return {'error': 'Suggestion not found'}

        suggestions = suggestion.suggestions
        selected = next((s for s in suggestions if s['user_id'] == user_id), None)
        if not selected:
            return {'error': 'Selected user not found in suggestions'}

        ticket = suggestion.ticket
        assignee = User.objects.get(id=user_id)

        suggestion.status = 'approved'
        suggestion.manager_approved_choice = manager
        suggestion.manager_notes = notes
        suggestion.save()

        # Record assignment history
        AssignmentHistory.objects.create(
            ticket=ticket,
            suggested_by_ai=manager,
            assigned_by=manager,
            assigned_to=assignee,
            was_ai_suggestion=True,
            ai_confidence=selected.get('score', 0),
            manager_approved=True,
            ai_reasoning=selected.get('reasoning', ''),
            manager_notes=notes,
        )

        # Assign the ticket
        ticket.assignee = assignee
        ticket.save()

        # Update developer profile
        profile, _ = DeveloperProfile.objects.get_or_create(user=assignee)
        profile.current_workload = Ticket.objects.filter(
            assignee=assignee, is_active=True
        ).exclude(status__in=['done', 'closed']).count()
        profile.save()

        return {
            'success': True,
            'ticket_id': ticket.id,
            'ticket_code': ticket.ticket_id,
            'assigned_to': assignee.username,
            'message': f'Ticket {ticket.ticket_id} assigned to {assignee.username}',
        }

    def reject(self, suggestion_id: int, manager: User, notes: str = '') -> Dict:
        """Manager rejects AI suggestion."""
        try:
            suggestion = AIAssignmentSuggestion.objects.get(id=suggestion_id)
        except AIAssignmentSuggestion.DoesNotExist:
            return {'error': 'Suggestion not found'}

        suggestion.status = 'rejected'
        suggestion.manager_approved_choice = manager
        suggestion.manager_notes = notes
        suggestion.save()

        return {'success': True, 'message': 'Suggestion rejected'}

    def get_unassigned_tickets(self, user: User) -> list:
        """Get unassigned tickets for the user's organizations."""
        from organizations.models import Organization
        org_ids = Organization.objects.filter(
            memberships__user=user, memberships__is_active=True
        ).values_list('id', flat=True)

        tickets = Ticket.objects.filter(
            organization_id__in=org_ids,
            assignee__isnull=True,
            is_active=True,
        ).select_related('project').order_by('-created_at')[:20]

        return [
            {'id': t.id, 'ticket_id': t.ticket_id, 'title': t.title,
             'project': t.project.name, 'priority': t.priority, 'status': t.status}
            for t in tickets
        ]

    def get_assignment_stats(self, user: User) -> Dict:
        """Get AI assignment statistics for manager dashboard."""
        suggestions = AIAssignmentSuggestion.objects.filter(
            ticket__project__organization__memberships__user=user,
            ticket__project__organization__memberships__is_active=True
        )
        total = suggestions.count()
        approved = suggestions.filter(status='approved').count()
        rejected = suggestions.filter(status='rejected').count()

        return {
            'total_suggestions': total,
            'approved': approved,
            'rejected': rejected,
            'approval_rate': round((approved / total) * 100, 1) if total > 0 else 0,
            'pending': suggestions.filter(status='pending').count(),
        }
