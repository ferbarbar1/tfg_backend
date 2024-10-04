from rest_framework import serializers
from .models import Conversation, Message, Notification


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"

    def validate_participants(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least two participants."
            )
        return value


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value

    def validate(self, data):
        conversation = data.get("conversation")
        sender = data.get("sender")
        if sender not in conversation.participants.all():
            raise serializers.ValidationError(
                "Sender must be a participant in the conversation."
            )
        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Notification message cannot be empty.")
        return value

    def validate_type(self, value):
        if value not in dict(Notification.NOTIFICATION_TYPES).keys():
            raise serializers.ValidationError("Invalid notification type.")
        return value
