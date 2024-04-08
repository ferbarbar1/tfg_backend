from workers.models import Appointment
from .models import Service
from .serializers import AppointmentSerializer, ServiceSerializer
from rest_framework import viewsets, permissions


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = AppointmentSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ServiceSerializer
