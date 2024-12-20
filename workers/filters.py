from django_filters import rest_framework as filters
from .models import Schedule, Inform


class ScheduleFilter(filters.FilterSet):
    class Meta:
        model = Schedule
        fields = ["date", "available", "worker"]
