from django_filters import rest_framework as filters
from django.db.models import Count, Q
from .models import Conversation, Message


class ParticipantsFilter(filters.BaseCSVFilter, filters.NumberFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        # Convertir los valores a un conjunto de enteros
        participant_ids = set(map(int, value))
        # Filtrar las conversaciones que tienen exactamente los participantes especificados
        filtered_qs = qs.annotate(num_participants=Count("participants")).filter(
            num_participants=len(participant_ids)
        )
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
        fields = ["conversation"]
