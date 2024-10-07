from .models import Rating, Appointment, MedicalHistory
from .serializers import (
    RatingSerializer,
    AppointmentSerializer,
    MedicalHistorySerializer,
)
from rest_framework import viewsets, permissions
from .filters import RatingFilter, AppointmentFilter, MedicalHistoryFilter


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer
    filterset_class = AppointmentFilter


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer
    filterset_class = RatingFilter


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MedicalHistorySerializer
    filterset_class = MedicalHistoryFilter
