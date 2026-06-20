from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .services.ticket_classifier import TicketClassifier
from .services.priority_predictor import PriorityPredictor
from .services.assignee_suggester import AssigneeSuggester
from .services.chatbot import TicketChatbot
from .services.sentiment_analyzer import SentimentAnalyzer
from .services.similar_tickets import SimilarTicketFinder
from .services.response_generator import ResponseGenerator
from .services.search_enhancer import SearchEnhancer
from .models import AIAssignmentSuggestion, AIMetrics, DeveloperProfile
from .serializers import (
    ClassifyRequestSerializer, PredictPriorityRequestSerializer,
    ChatRequestSerializer, ApproveRequestSerializer, RejectRequestSerializer,
    AIMetricsSerializer, DeveloperProfileSerializer,
    AIAssignmentSuggestionSerializer,
)


# ============ TICKET CLASSIFICATION ============

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def classify_ticket(request):
    """Classify a ticket using AI."""
    serializer = ClassifyRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    classifier = TicketClassifier()
    result = classifier.classify(
        serializer.validated_data['title'],
        serializer.validated_data['description']
    )
    return Response(result)


# ============ PRIORITY PREDICTION ============

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_priority(request):
    """Predict ticket priority using AI."""
    serializer = PredictPriorityRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    predictor = PriorityPredictor()
    result = predictor.predict(
        serializer.validated_data['title'],
        serializer.validated_data['description']
    )
    return Response(result)


# ============ SMART ASSIGNMENT (MANAGER APPROVAL) ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def suggest_assignee(request, ticket_id):
    """Get AI-suggested assignees for a ticket."""
    suggester = AssigneeSuggester()
    result = suggester.get_suggestions(ticket_id)
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_suggestion(request):
    """Manager approves an AI assignment suggestion."""
    serializer = ApproveRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    suggester = AssigneeSuggester()
    result = suggester.approve(
        suggestion_id=serializer.validated_data['suggestion_id'],
        user_id=serializer.validated_data['user_id'],
        manager=request.user,
        notes=serializer.validated_data.get('notes', ''),
    )
    if 'error' in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_suggestion(request):
    """Manager rejects an AI assignment suggestion."""
    serializer = RejectRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    suggester = AssigneeSuggester()
    result = suggester.reject(
        suggestion_id=serializer.validated_data['suggestion_id'],
        manager=request.user,
        notes=serializer.validated_data.get('notes', ''),
    )
    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unassigned_tickets(request):
    """Get unassigned tickets for the current user's organizations."""
    suggester = AssigneeSuggester()
    tickets = suggester.get_unassigned_tickets(request.user)
    return Response({'count': len(tickets), 'results': tickets})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def assignment_stats(request):
    """Get AI assignment statistics."""
    suggester = AssigneeSuggester()
    stats = suggester.get_assignment_stats(request.user)
    return Response(stats)


# ============ CHATBOT ============

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat(request):
    """Chat with the AI assistant."""
    serializer = ChatRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    chatbot = TicketChatbot()
    result = chatbot.chat(
        serializer.validated_data['message'],
        request.user.id
    )
    return Response(result)


# ============ SENTIMENT ANALYSIS ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analyze_sentiment(request, ticket_id):
    """Analyze sentiment for a ticket."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_ticket(ticket_id)
    return Response(result)


# ============ SIMILAR TICKETS ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def similar_tickets(request, ticket_id):
    """Find tickets similar to the given ticket."""
    finder = SimilarTicketFinder()
    results = finder.find(ticket_id)
    return Response({'count': len(results), 'results': results})


# ============ RESPONSE GENERATION ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_response(request, ticket_id):
    """Generate a draft response for a ticket."""
    generator = ResponseGenerator()
    result = generator.generate(ticket_id)
    return Response(result)


# ============ ENHANCED SEARCH ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def enhance_search(request):
    """AI-enhanced ticket search."""
    query = request.query_params.get('q', '')
    if len(query) < 2:
        return Response(
            {'error': 'Query must be at least 2 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    enhancer = SearchEnhancer()
    results = enhancer.search(query, request.user)
    return Response({'count': len(results), 'results': results})


# ============ AI METRICS ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_metrics(request):
    """Get AI usage metrics."""
    hours = int(request.query_params.get('hours', 24))
    stats = AIMetrics.get_stats(hours)
    recent = AIMetrics.objects.order_by('-created_at')[:50]
    return Response({
        'stats': stats,
        'recent': AIMetricsSerializer(recent, many=True).data,
    })


# ============ DEVELOPER PROFILE ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def developer_profiles(request):
    """Get developer profiles."""
    profiles = DeveloperProfile.objects.select_related('user').all()
    return Response({
        'count': profiles.count(),
        'results': DeveloperProfileSerializer(profiles, many=True).data,
    })
