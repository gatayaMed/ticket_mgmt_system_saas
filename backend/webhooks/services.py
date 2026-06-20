import requests
import json
import time
from django.utils import timezone
from .models import Webhook, WebhookLog


class WebhookService:
    @staticmethod
    def dispatch_event(organization_id, event, payload):
        """Dispatch a webhook event to all matching webhooks"""
        webhooks = Webhook.objects.filter(
            organization_id=organization_id,
            is_active=True
        )

        results = []
        for webhook in webhooks:
            if event not in webhook.events:
                continue

            start_time = time.time()
            try:
                signature = webhook.generate_signature(json.dumps(payload))
                response = requests.post(
                    webhook.url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-TicketSaaS-Event': event,
                        'X-Signature': signature,
                    },
                    timeout=10
                )

                duration = time.time() - start_time
                WebhookLog.objects.create(
                    webhook=webhook,
                    event=event,
                    payload=payload,
                    response_status=response.status_code,
                    response_body=response.text[:1000],
                    duration=duration
                )

                webhook.last_triggered = timezone.now()
                webhook.last_response = {
                    'status': response.status_code,
                    'duration': round(duration, 2)
                }
                webhook.failure_count = 0
                webhook.save(update_fields=['last_triggered', 'last_response', 'failure_count'])

                results.append({
                    'webhook_id': webhook.id,
                    'webhook_name': webhook.name,
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'duration': round(duration, 2)
                })

            except requests.exceptions.RequestException as e:
                duration = time.time() - start_time
                WebhookLog.objects.create(
                    webhook=webhook,
                    event=event,
                    payload=payload,
                    response_status=0,
                    response_body=str(e)[:1000],
                    duration=duration
                )

                webhook.failure_count += 1
                webhook.last_triggered = timezone.now()
                if webhook.failure_count >= 10:
                    webhook.is_active = False
                webhook.save(update_fields=['failure_count', 'last_triggered', 'is_active'])

                results.append({
                    'webhook_id': webhook.id,
                    'webhook_name': webhook.name,
                    'success': False,
                    'error': str(e)[:200],
                    'duration': round(duration, 2)
                })

        return results

    @staticmethod
    def dispatch_ticket_event(ticket, event):
        """Convenience method to dispatch ticket events"""
        payload = {
            'event': event,
            'ticket': {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'title': ticket.title,
                'status': ticket.status,
                'priority': ticket.priority,
                'ticket_type': ticket.ticket_type,
                'assignee': ticket.assignee.username if ticket.assignee else None,
                'project': ticket.project.name if ticket.project else None,
                'due_date': ticket.due_date.isoformat() if ticket.due_date else None,
                'updated_at': ticket.updated_at.isoformat()
            }
        }
        return WebhookService.dispatch_event(ticket.organization_id, event, payload)

    @staticmethod
    def dispatch_project_event(project, event):
        """Convenience method to dispatch project events"""
        payload = {
            'event': event,
            'project': {
                'id': project.id,
                'name': project.name,
                'slug': project.slug,
                'status': project.status,
                'priority': project.priority,
                'progress': project.progress,
                'updated_at': project.updated_at.isoformat()
            }
        }
        return WebhookService.dispatch_event(project.organization_id, event, payload)

    @staticmethod
    def dispatch_sprint_event(sprint, event):
        """Convenience method to dispatch sprint events"""
        payload = {
            'event': event,
            'sprint': {
                'id': sprint.id,
                'name': sprint.name,
                'project': sprint.project.name,
                'status': sprint.status,
                'progress': sprint.progress,
                'start_date': sprint.start_date.isoformat(),
                'end_date': sprint.end_date.isoformat()
            }
        }
        return WebhookService.dispatch_event(sprint.project.organization_id, event, payload)
