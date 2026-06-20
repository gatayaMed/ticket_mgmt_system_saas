import os
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from organizations.models import Organization, Membership, Invitation
from projects.models import Project, ProjectMember
from tickets.models import Ticket, TicketHistory
from comments.models import Comment
from attachments.models import Attachment

def create_dummy_data():
    print("🚀 Creating dummy data...")
    
    # Create users
    users = []
    user_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'password': 'Test123!'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'Test123!'},
        {'username': 'bob_wilson', 'email': 'bob@example.com', 'password': 'Test123!'},
        {'username': 'alice_brown', 'email': 'alice@example.com', 'password': 'Test123!'},
        {'username': 'charlie_davis', 'email': 'charlie@example.com', 'password': 'Test123!'},
        {'username': 'emma_thomas', 'email': 'emma@example.com', 'password': 'Test123!'},
        {'username': 'mike_johnson', 'email': 'mike@example.com', 'password': 'Test123!'},
        {'username': 'sarah_williams', 'email': 'sarah@example.com', 'password': 'Test123!'},
    ]
    
    print("👤 Creating users...")
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'is_active': True
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"  ✅ Created user: {user.username}")
        users.append(user)
    
    # Create organizations
    orgs = []
    org_data = [
        {'name': 'TechCorp', 'description': 'Leading technology solutions provider'},
        {'name': 'InnovateLabs', 'description': 'Innovation and research lab'},
        {'name': 'CloudMasters', 'description': 'Cloud infrastructure experts'},
        {'name': 'DataFlow Inc', 'description': 'Data analytics and insights'},
        {'name': 'SecureNet', 'description': 'Cybersecurity solutions'},
    ]
    
    print("🏢 Creating organizations...")
    for data in org_data:
        org, created = Organization.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['description'],
                'created_by': users[0]
            }
        )
        if created:
            org.slug = org.name.lower().replace(' ', '-')
            org.save()
            print(f"  ✅ Created organization: {org.name}")
        orgs.append(org)
    
    # Add members to organizations with different roles
    print("👥 Adding members to organizations...")
    roles = ['admin', 'manager', 'developer', 'developer', 'developer', 'support', 'viewer']
    
    for idx, org in enumerate(orgs):
        # Skip first organization (we'll handle it separately)
        if idx == 0:
            continue
            
        # Add 3-5 random users to each organization
        for i in range(3, min(len(users), 6)):
            role = random.choice(roles)
            Membership.objects.get_or_create(
                user=users[i],
                organization=org,
                defaults={
                    'role': role,
                    'invited_by': users[0],
                    'is_active': True
                }
            )
        print(f"  ✅ Added members to {org.name}")
    
    # For the first organization, add all users with specific roles
    main_org = orgs[0]
    print(f"  ✅ Adding all users to {main_org.name}...")
    for i, user in enumerate(users):
        if i == 0:
            role = 'admin'
        elif i == 1:
            role = 'manager'
        elif i < 4:
            role = 'developer'
        elif i < 6:
            role = 'support'
        else:
            role = 'viewer'
        
        Membership.objects.get_or_create(
            user=user,
            organization=main_org,
            defaults={
                'role': role,
                'invited_by': users[0],
                'is_active': True
            }
        )
    
    # Create projects
    projects = []
    project_data = [
        {'name': 'E-Commerce Platform', 'description': 'Building a scalable e-commerce platform'},
        {'name': 'Mobile App Development', 'description': 'Cross-platform mobile application'},
        {'name': 'AI Chatbot', 'description': 'Intelligent customer support chatbot'},
        {'name': 'Data Analytics Dashboard', 'description': 'Real-time analytics dashboard'},
        {'name': 'Cloud Migration', 'description': 'Migrating legacy systems to cloud'},
        {'name': 'Security Audit', 'description': 'Comprehensive security audit'},
        {'name': 'API Gateway', 'description': 'Building API gateway for microservices'},
        {'name': 'DevOps Pipeline', 'description': 'CI/CD pipeline implementation'},
    ]
    
    print("📊 Creating projects...")
    for data in project_data:
        # Randomly assign to different organizations
        org = random.choice(orgs[:3])  # Use first 3 organizations
        project, created = Project.objects.get_or_create(
            name=data['name'],
            organization=org,
            defaults={
                'description': data['description'],
                'slug': data['name'].lower().replace(' ', '-'),
                'created_by': random.choice(users[:3]),
                'status': random.choice(['active', 'active', 'active', 'paused', 'completed']),
                'priority': random.choice(['low', 'medium', 'medium', 'high', 'critical']),
                'start_date': timezone.now() - timedelta(days=random.randint(10, 60)),
                'due_date': timezone.now() + timedelta(days=random.randint(20, 90)),
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ Created project: {project.name}")
        projects.append(project)
    
    # Add members to projects
    print("👥 Adding members to projects...")
    for project in projects:
        # Get all members of the project's organization
        org_members = Membership.objects.filter(
            organization=project.organization,
            is_active=True
        ).select_related('user')
        
        # Add 3-6 members to each project
        selected_members = random.sample(list(org_members), min(len(org_members), random.randint(3, 6)))
        
        for member in selected_members:
            role = random.choice(['project_lead', 'developer', 'developer', 'qa', 'viewer'])
            ProjectMember.objects.get_or_create(
                project=project,
                user=member.user,
                defaults={
                    'role': role,
                    'is_active': True
                }
            )
        print(f"  ✅ Added {len(selected_members)} members to {project.name}")
    
    # Create tickets
    print("🎫 Creating tickets...")
    ticket_titles = [
        "Fix login authentication bug",
        "Implement payment gateway",
        "Add user profile page",
        "Optimize database queries",
        "Fix mobile responsiveness",
        "Implement search functionality",
        "Add email notifications",
        "Fix security vulnerability",
        "Implement API rate limiting",
        "Add dark mode support",
        "Fix image upload issue",
        "Implement real-time notifications",
        "Add export functionality",
        "Fix broken links",
        "Optimize loading speed",
        "Add multi-language support",
        "Implement social login",
        "Fix data validation issues",
        "Add reporting dashboard",
        "Implement user roles",
    ]
    
    statuses = ['backlog', 'todo', 'in_progress', 'review', 'done', 'closed']
    priorities = ['low', 'medium', 'medium', 'high', 'critical']
    ticket_types = ['bug', 'feature', 'task', 'improvement', 'epic']
    
    ticket_count = 0
    for project in projects:
        # Create 5-15 tickets per project
        num_tickets = random.randint(5, 15)
        project_members = ProjectMember.objects.filter(
            project=project,
            is_active=True
        ).select_related('user')
        
        if not project_members:
            continue
            
        for i in range(num_tickets):
            title = random.choice(ticket_titles) + f" (Project {project.name})"
            status = random.choice(statuses[:4])  # Don't start with closed
            
            # Get random assignee
            assignee = random.choice(project_members).user
            
            ticket = Ticket.objects.create(
                title=title,
                description=f"Detailed description for: {title}\n\nThis is a test ticket created for demonstration purposes.",
                project=project,
                organization=project.organization,
                status=status,
                priority=random.choice(priorities),
                ticket_type=random.choice(ticket_types),
                assignee=assignee,
                created_by=random.choice(project_members[:3]).user,
                due_date=timezone.now() + timedelta(days=random.randint(5, 45)),
                estimated_hours=random.randint(1, 20),
                is_active=True
            )
            
            ticket_count += 1
            
            # Create ticket history
            actions = [
                ('created', f"Created ticket {ticket.ticket_id}"),
            ]
            
            # Randomly add status changes
            if random.random() > 0.3:
                status_history = ['todo', 'in_progress', 'review', 'done']
                for new_status in status_history[:random.randint(1, 3)]:
                    TicketHistory.objects.create(
                        ticket=ticket,
                        user=random.choice(project_members).user,
                        action='status_changed',
                        old_value={'status': ticket.status},
                        new_value={'status': new_status},
                        description=f"Status changed to {new_status}"
                    )
                    ticket.status = new_status
                    ticket.save()
            
            # Randomly add assignment changes
            if random.random() > 0.5:
                new_assignee = random.choice(project_members).user
                TicketHistory.objects.create(
                    ticket=ticket,
                    user=random.choice(project_members).user,
                    action='assigned',
                    old_value={'assignee': ticket.assignee.id if ticket.assignee else None},
                    new_value={'assignee': new_assignee.id},
                    description=f"Ticket assigned to {new_assignee.username}"
                )
                ticket.assignee = new_assignee
                ticket.save()
            
            # If status is done, set completed_at
            if ticket.status == 'done':
                ticket.completed_at = timezone.now() - timedelta(days=random.randint(1, 10))
                ticket.save()
            
            if ticket_count % 10 == 0:
                print(f"  ✅ Created {ticket_count} tickets...")
    
    print(f"  ✅ Total tickets created: {ticket_count}")
    
    # Create comments
    print("💬 Creating comments...")
    comment_texts = [
        "This is a critical issue that needs immediate attention.",
        "I can work on this tomorrow morning.",
        "Great progress! Keep it up.",
        "Can you provide more details about this?",
        "I've tested this and it works fine.",
        "This needs to be prioritized.",
        "I'm having issues reproducing this bug.",
        "Looks good to me!",
        "Can we add this to the next sprint?",
        "I'll review this today.",
        "This is ready for QA testing.",
        "Excellent work on this ticket!",
        "I think we should reconsider the approach.",
        "This has been resolved in the latest update.",
        "Can we get an ETA on this?",
        "I've assigned this to John for review.",
        "This is blocking other features.",
        "I'll create a PR for this today.",
        "This looks like a duplicate of ticket #123.",
        "I've updated the documentation for this.",
    ]
    
    comment_count = 0
    tickets = Ticket.objects.filter(is_active=True)
    for ticket in tickets[:100]:  # Add comments to first 100 tickets
        num_comments = random.randint(0, 5)
        project_members = ProjectMember.objects.filter(
            project=ticket.project,
            is_active=True
        ).select_related('user')
        
        for _ in range(num_comments):
            user = random.choice(project_members).user if project_members else users[0]
            Comment.objects.create(
                ticket=ticket,
                user=user,
                content=random.choice(comment_texts),
                is_active=True
            )
            comment_count += 1
        
        if comment_count % 20 == 0:
            print(f"  ✅ Created {comment_count} comments...")
    
    print(f"  ✅ Total comments created: {comment_count}")
    
    # Create attachments (simulated)
    print("📎 Creating attachments...")
    attachment_names = [
        'screenshot.png', 'document.pdf', 'error_log.txt',
        'config.yaml', 'diagram.svg', 'test_data.csv',
        'requirements.txt', 'docker-compose.yml', 'readme.md'
    ]
    
    attachment_count = 0
    for ticket in tickets[:50]:  # Add attachments to first 50 tickets
        num_attachments = random.randint(0, 3)
        for _ in range(num_attachments):
            try:
                # Create a dummy file content
                from django.core.files.base import ContentFile
                filename = random.choice(attachment_names)
                content = f"Sample content for {filename}".encode()
                file = ContentFile(content, name=filename)
                
                Attachment.objects.create(
                    ticket=ticket,
                    user=ticket.created_by or users[0],
                    file=file,
                    description=f"Attachment for {ticket.ticket_id}",
                    is_active=True
                )
                attachment_count += 1
            except Exception as e:
                pass  # Skip if file creation fails
    
    print(f"  ✅ Total attachments created: {attachment_count}")
    
    # Create sprints for projects
    print("🏃 Creating sprints...")
    from sprints.models import Sprint, SprintHistory
    
    sprint_count = 0
    sprint_names = [
        "Sprint Alpha", "Sprint Beta", "Sprint Gamma",
        "Sprint Delta", "Sprint Epsilon", "Sprint Zeta",
        "Sprint Eta", "Sprint Theta", "Sprint Iota",
    ]
    
    for project in projects[:5]:  # Add sprints to first 5 projects
        num_sprints = random.randint(1, 3)
        project_tickets = list(Ticket.objects.filter(project=project, is_active=True))
        
        for i in range(num_sprints):
            sprint_name = random.choice(sprint_names)
            start = timezone.now() - timedelta(days=random.randint(5, 30))
            end = start + timedelta(days=random.randint(7, 21))
            status = random.choice(['planning', 'active', 'completed'])
            
            sprint, created = Sprint.objects.get_or_create(
                name=sprint_name,
                project=project,
                defaults={
                    'goal': f'Complete sprint goals for {sprint_name}',
                    'start_date': start,
                    'end_date': end,
                    'status': status,
                    'created_by': random.choice(users[:3]),
                    'is_active': True,
                    'completed_at': end if status == 'completed' else None
                }
            )
            
            if created and project_tickets:
                # Add 3-7 random tickets to sprint
                num_tickets = min(random.randint(3, 7), len(project_tickets))
                sprint_tickets = random.sample(project_tickets, num_tickets)
                sprint.tickets.add(*sprint_tickets)
                
                # Create sprint history
                SprintHistory.objects.create(
                    sprint=sprint,
                    action='created',
                    user=sprint.created_by,
                    description=f'Sprint created with {num_tickets} tickets'
                )
                
                if status == 'active':
                    SprintHistory.objects.create(
                        sprint=sprint,
                        action='started',
                        user=sprint.created_by,
                        description='Sprint started'
                    )
                elif status == 'completed':
                    SprintHistory.objects.create(
                        sprint=sprint,
                        action='started',
                        user=sprint.created_by,
                        description='Sprint started'
                    )
                    SprintHistory.objects.create(
                        sprint=sprint,
                        action='completed',
                        user=sprint.created_by,
                        description='Sprint completed'
                    )
                
                sprint_count += 1
                print(f"  ✅ Created sprint: {sprint_name} ({num_tickets} tickets)")
    
    print(f"  ✅ Total sprints created: {sprint_count}")
    
    # Create in-app notifications
    print("🔔 Creating notifications...")
    from notifications.models import Notification, NotificationPreference
    
    notif_count = 0
    notif_types = ['ticket_created', 'ticket_assigned', 'ticket_status_changed', 'comment_added', 'ticket_due', 'ticket_overdue']
    notif_titles = {
        'ticket_created': 'New ticket created',
        'ticket_assigned': 'Ticket assigned to you',
        'ticket_status_changed': 'Ticket status updated',
        'comment_added': 'New comment on ticket',
        'ticket_due': 'Ticket due soon',
        'ticket_overdue': 'Ticket is overdue',
    }
    
    for user in users:
        # Create notification preferences
        NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_enabled': True,
                'slack_enabled': False,
                'ticket_created': True,
                'ticket_assigned': True,
                'ticket_status_changed': True,
                'comment_added': True,
                'mentions': True,
                'ticket_due_reminders': True,
                'daily_digest': False,
            }
        )
        
        # Create 3-8 notifications per user
        num_notifs = random.randint(3, 8)
        for _ in range(num_notifs):
            ntype = random.choice(notif_types)
            is_read = random.random() > 0.4  # 60% chance of unread
            
            Notification.objects.create(
                user=user,
                type=ntype,
                channel='in_app',
                title=notif_titles[ntype],
                message=f'Sample notification for {user.username}: {notif_titles[ntype]}',
                link=f'/tickets/{random.randint(1, 50)}',
                is_read=is_read,
                read_at=timezone.now() if is_read else None,
                metadata={'ticket_id': random.randint(1, 50)}
            )
            notif_count += 1
    
    print(f"  ✅ Total notifications created: {notif_count}")
    
    # Create webhooks for organizations
    print("🔗 Creating webhooks...")
    from webhooks.models import Webhook, WebhookLog
    
    webhook_count = 0
    webhook_names = ['Slack Integration', 'Discord Bot', 'Teams Notifier', 'Custom CI/CD', 'Zapier Hook', 'GitHub Sync']
    
    for org in orgs[:3]:
        num_hooks = random.randint(1, 2)
        for _ in range(num_hooks):
            events = random.sample(
                ['ticket.created', 'ticket.updated', 'ticket.status_changed', 'ticket.assigned', 'comment.added', 'project.created', 'sprint.started', 'sprint.completed'],
                random.randint(2, 5)
            )
            
            webhook = Webhook.objects.create(
                organization=org,
                name=random.choice(webhook_names),
                url=f'https://hooks.example.com/{org.slug}/{random.randint(1000, 9999)}',
                events=events,
                is_active=random.random() > 0.2,
                last_triggered=timezone.now() - timedelta(days=random.randint(0, 3)) if random.random() > 0.5 else None
            )
            
            # Create some webhook logs
            if webhook.last_triggered:
                for _ in range(random.randint(1, 5)):
                    WebhookLog.objects.create(
                        webhook=webhook,
                        event=random.choice(events),
                        payload={'event': random.choice(events), 'data': {'test': True}},
                        response_status=random.choice([200, 200, 200, 201, 400, 500]),
                        response_body='{"status": "ok"}',
                        duration=round(random.uniform(0.1, 2.5), 2)
                    )
            
            webhook_count += 1
            print(f"  ✅ Created webhook: {webhook.name} ({len(events)} events)")
    
    print(f"  ✅ Total webhooks created: {webhook_count}")
    
    # Create activity feed entries
    print("📜 Creating activity feed...")
    from activity.models import Activity, ActivityFeed
    
    activity_count = 0
    activity_actions = ['created', 'updated', 'deleted', 'status_changed', 'assigned', 'commented', 'completed']
    activity_descriptions = {
        'created': 'created a new ticket',
        'updated': 'updated ticket details',
        'deleted': 'removed a ticket',
        'status_changed': 'changed ticket status',
        'assigned': 'reassigned the ticket',
        'commented': 'added a comment',
        'completed': 'completed the ticket',
    }
    
    for user in users:
        num_activities = random.randint(2, 6)
        for _ in range(num_activities):
            action = random.choice(activity_actions)
            org = random.choice(orgs)
            
            Activity.objects.create(
                user=user,
                organization=org,
                action=action,
                description=f'{user.username} {activity_descriptions[action]}',
                metadata={'ticket_id': random.randint(1, 50), 'project_id': random.choice(projects).id}
            )
            activity_count += 1
    
    print(f"  ✅ Total activities created: {activity_count}")
    

    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    print(f"👤 Users: {User.objects.count()}")
    print(f"🏢 Organizations: {Organization.objects.count()}")
    print(f"👥 Memberships: {Membership.objects.count()}")
    print(f"📊 Projects: {Project.objects.count()}")
    print(f"👤 Project Members: {ProjectMember.objects.count()}")
    print(f"🎫 Tickets: {Ticket.objects.count()}")
    print(f"📝 Ticket History: {TicketHistory.objects.count()}")
    print(f"💬 Comments: {Comment.objects.count()}")
    print(f"📎 Attachments: {Attachment.objects.count()}")
    print(f"🏃 Sprints: {Sprint.objects.count()}")
    print(f"📝 Sprint History: {SprintHistory.objects.count()}")
    print(f"🔔 Notifications: {Notification.objects.count()}")
    print(f"🔗 Webhooks: {Webhook.objects.count()}")
    print(f"🔗 Webhook Logs: {WebhookLog.objects.count()}")
    print(f"📜 Activities: {Activity.objects.count()}")
    print("="*50)
    print("🎉 Dummy data creation completed!")

if __name__ == '__main__':
    create_dummy_data()