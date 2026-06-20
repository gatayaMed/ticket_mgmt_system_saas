# notifications/services.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
import requests
import json
from .models import Notification, NotificationPreference

User = get_user_model()

class NotificationService:
    @staticmethod
    def send_email_notification(user, subject, message, html_message=None):
        """Send email notification"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message or message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False

    @staticmethod
    def send_slack_notification(webhook_url, message):
        """Send Slack notification"""
        try:
            payload = {
                'text': message,
                'username': 'TicketSaaS Bot',
                'icon_emoji': ':ticket:'
            }
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False

    @staticmethod
    def create_notification(user, type, title, message, link=None, metadata=None):
        """Create in-app notification"""
        notification = Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            link=link,
            metadata=metadata or {}
        )
        return notification

    @staticmethod
    def send_notification(user, type, title, message, link=None, metadata=None):
        """Send notification through all enabled channels"""
        try:
            preferences = NotificationPreference.objects.get(user=user)
        except NotificationPreference.DoesNotExist:
            preferences = None

        # Create in-app notification
        notification = NotificationService.create_notification(
            user, type, title, message, link, metadata
        )

        # Send email if enabled
        if preferences and preferences.email_enabled:
            html_message = render_to_string('notifications/email_template.html', {
                'title': title,
                'message': message,
                'link': link,
                'user': user
            })
            plain_message = strip_tags(html_message)
            NotificationService.send_email_notification(
                user,
                f"[TicketSaaS] {title}",
                plain_message,
                html_message
            )

        # Send Slack if enabled
        if preferences and preferences.slack_enabled and preferences.slack_webhook_url:
            slack_message = f"*{title}*\n{message}"
            if link:
                slack_message += f"\n<{link}|View Details>"
            NotificationService.send_slack_notification(
                preferences.slack_webhook_url,
                slack_message
            )

        return notification

    @staticmethod
    def get_unread_count(user):
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def mark_all_as_read(user):
        updated = Notification.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return updated

    @staticmethod
    def create_ticket_notification(ticket, user, action):
        """Helper to create ticket notifications"""
        titles = {
            'created': f"New Ticket: {ticket.ticket_id}",
            'assigned': f"Ticket {ticket.ticket_id} Assigned",
            'status_changed': f"Ticket {ticket.ticket_id} Status Changed",
            'updated': f"Ticket {ticket.ticket_id} Updated"
        }
        
        messages = {
            'created': f"{user.username} created ticket {ticket.ticket_id}",
            'assigned': f"{user.username} assigned ticket {ticket.ticket_id} to {ticket.assignee.username if ticket.assignee else 'unassigned'}",
            'status_changed': f"{user.username} changed status to {ticket.get_status_display()}",
            'updated': f"{user.username} updated ticket {ticket.ticket_id}"
        }
        
        return NotificationService.send_notification(
            user=ticket.assignee or ticket.created_by,
            type=f'ticket_{action}',
            title=titles.get(action, f"Ticket {ticket.ticket_id}"),
            message=messages.get(action, f"Ticket {ticket.ticket_id} was updated"),
            link=f"/tickets/{ticket.id}",
            metadata={'ticket_id': ticket.id, 'ticket_number': ticket.ticket_id}
        )