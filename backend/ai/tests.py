"""
Tests for AI integration app.
Run with: python manage.py test ai
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from projects.models import Project
from organizations.models import Organization
from .models import (
    DeveloperProfile, AIAssignmentSuggestion,
    AssignmentHistory, AIMetrics
)
from .services.ticket_classifier import TicketClassifier
from .services.chatbot import TicketChatbot
from .services.sentiment_analyzer import SentimentAnalyzer
from .core.config import AIConfig

User = get_user_model()


class AIConfigTest(TestCase):
    """Test AI configuration."""

    def test_config_loaded(self):
        self.assertIsNotNone(AIConfig.get_enabled_providers())
        self.assertIsInstance(AIConfig.is_cache_enabled(), bool)

    def test_default_provider(self):
        providers = AIConfig.get_enabled_providers()
        if providers:
            provider = AIConfig.get_default_provider()
            self.assertIn(provider, providers)

    def test_cache_settings(self):
        ttl = AIConfig.get_cache_ttl()
        self.assertGreater(ttl, 0)

    def test_assignment_settings(self):
        max_sug = AIConfig.get_max_suggestions()
        min_conf = AIConfig.get_min_confidence()
        self.assertGreater(max_sug, 0)
        self.assertGreaterEqual(min_conf, 0)


class AIModelsTest(TestCase):
    """Test AI models."""

    def setUp(self):
        self.user = User.objects.create_user(username='ai_test_user', password='test123')

    def test_developer_profile_creation(self):
        profile, created = DeveloperProfile.objects.get_or_create(
            user=self.user,
            defaults={'skills': {'python': 5}, 'years_experience': 3}
        )
        self.assertTrue(created)
        self.assertEqual(profile.skills['python'], 5)

    def test_metrics_recording(self):
        metric = AIMetrics.record('deepseek', 'classify', 0.5, tokens=100)
        self.assertEqual(metric.provider, 'deepseek')
        self.assertEqual(metric.tokens_used, 100)

    def test_metrics_stats(self):
        AIMetrics.record('deepseek', 'test', 0.3, tokens=50)
        AIMetrics.record('deepseek', 'test', 0.7, tokens=30, success=False, error='timeout')
        stats = AIMetrics.get_stats(hours=1)
        self.assertIn('total_requests', stats)
        self.assertIn('avg_response_time', stats)


class TicketClassifierTest(TestCase):
    """Test ticket classifier service."""

    def setUp(self):
        self.user = User.objects.create_user(username='classifier_test', password='test123')
        self.org = Organization.objects.create(name='TestOrg', created_by=self.user)
        self.project = Project.objects.create(
            name='TestProject', organization=self.org, created_by=self.user,
            slug='test-project'
        )

    def test_classifier_initialization(self):
        classifier = TicketClassifier()
        self.assertIsNotNone(classifier.orchestrator)
        self.assertEqual(classifier.CATEGORIES, ['bug', 'feature', 'task', 'improvement', 'epic'])


class ChatbotTest(TestCase):
    """Test chatbot service."""

    def setUp(self):
        self.user = User.objects.create_user(username='chatbot_test', password='test123')

    def test_chatbot_initialization(self):
        chatbot = TicketChatbot()
        self.assertIsNotNone(chatbot.orchestrator)
        self.assertIsNotNone(chatbot.SYSTEM_PROMPT)

    def test_extract_actions(self):
        chatbot = TicketChatbot()
        actions = chatbot._extract_actions("Let's create a ticket for the login bug")
        self.assertTrue(any(a['type'] == 'create_ticket' for a in actions))

        actions = chatbot._extract_actions("Search for payment issues")
        self.assertTrue(any(a['type'] == 'search' for a in actions))


class SentimentAnalyzerTest(TestCase):
    """Test sentiment analyzer."""

    def test_initialization(self):
        analyzer = SentimentAnalyzer()
        self.assertEqual(
            analyzer.LABELS,
            ['positive', 'neutral', 'negative', 'frustrated', 'urgent']
        )
