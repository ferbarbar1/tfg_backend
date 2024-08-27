from django_filters import rest_framework as filters
from .models import Conversation, Message, Notification


class ParticipantsFilter(filters.BaseCSVFilter, filters.NumberFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        participant_ids = set(map(int, value))
        filtered_qs = qs
        for participant_id in participant_ids:
            filtered_qs = filtered_qs.filter(participants__id=participant_id)
        return filtered_qs.distinct()


class ConversationFilter(filters.FilterSet):
    participants = ParticipantsFilter(field_name="participants__id", lookup_expr="in")

    class Meta:
        model = Conversation
        fields = ["participants"]


class MessageFilter(filters.FilterSet):
    class Meta:
        model = Message
        fields = ["conversation", "sender"]


class NotificationFilter(filters.FilterSet):
    class Meta:
        model = Notification
        fields = ["user", "is_read"]
