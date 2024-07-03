from .models import Schedule, Inform
from .serializers import ScheduleSerializer, InformSerializer
from .filters import ScheduleFilter
from rest_framework import viewsets, permissions


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ScheduleSerializer
    filterset_class = ScheduleFilter


class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = InformSerializer
