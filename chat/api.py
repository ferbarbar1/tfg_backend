from .models import Conversation, Message, Notification
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    NotificationSerializer,
)
from .filters import ConversationFilter, MessageFilter, NotificationFilter
from rest_framework import viewsets, permissions


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by("-last_message")
    permission_classes = [permissions.AllowAny]
    serializer_class = ConversationSerializer
    filterset_class = ConversationFilter


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = MessageSerializer
    filterset_class = MessageFilter


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = NotificationSerializer
    filterset_class = NotificationFilter
