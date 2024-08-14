from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Conversation, Message


class ParticipantsFilter(filters.BaseCSVFilter, filters.NumberFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        query = Q()
        for participant_id in value:
            query |= Q(participants__id=participant_id)
        return qs.filter(query).distinct()


class ConversationFilter(filters.FilterSet):
    participants = ParticipantsFilter(field_name="participants__id", lookup_expr="in")

    class Meta:
        model = Conversation
        fields = ["participants"]


class MessageFilter(filters.FilterSet):
    class Meta:
        model = Message
        fields = ["conversation"]
