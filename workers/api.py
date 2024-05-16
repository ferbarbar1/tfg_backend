from .models import Schedule
from .serializers import ScheduleSerializer
from .filters import ScheduleFilter
from rest_framework import viewsets, permissions


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ScheduleSerializer
    filterset_class = ScheduleFilter
