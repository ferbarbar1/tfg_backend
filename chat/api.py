from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .filters import ConversationFilter, MessageFilter
from rest_framework import viewsets, permissions


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ConversationSerializer
    filterset_class = ConversationFilter


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = MessageSerializer
    filterset_class = MessageFilter
