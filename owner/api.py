from workers.models import Appointment
from .models import Service
from .serializers import AppointmentSerializer, ServiceSerializer
from rest_framework import viewsets, permissions
from .filters import AppointmentFilter


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = AppointmentSerializer
    filterset_class = AppointmentFilter


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ServiceSerializer
