from .models import Rating
from .models import Appointment
from .serializers import RatingSerializer, AppointmentSerializer
from rest_framework import viewsets, permissions
from .filters import RatingFilter, AppointmentFilter


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = AppointmentSerializer
    filterset_class = AppointmentFilter


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RatingSerializer
    filterset_class = RatingFilter
