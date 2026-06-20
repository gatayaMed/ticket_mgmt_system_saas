# organizations/services/email_service.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime

class EmailService:
    """Service for sending email notifications"""
    
    @staticmethod
    def send_invitation_email(invitation, request=None):
        """
        Send invitation email to the invited user
        """
        # Generate accept URL
        if request:
            accept_url = request.build_absolute_uri(
                f'/api/organizations/invitations/accept/?token={invitation.token}'
            )
        else:
            # Fallback URL
            accept_url = f"{settings.FRONTEND_URL}/accept-invitation/{invitation.token}"
        
        # Prepare context
        context = {
            'user_name': invitation.email.split('@')[0],
            'inviter_name': invitation.invited_by.get_full_name() or invitation.invited_by.username,
            'inviter_email': invitation.invited_by.email,
            'organization_name': invitation.organization.name,
            'role': invitation.get_role_display(),
            'expires_at': invitation.expires_at,
            'accept_url': accept_url,
            'current_year': datetime.now().year,
        }
        
        # Render HTML email
        html_message = render_to_string('emails/invitation_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        subject = f"Invitation to join {invitation.organization.name}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invitation.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        # Update invitation
        invitation.email_sent_at = datetime.now()
        invitation.save(update_fields=['email_sent_at'])
        
        return True