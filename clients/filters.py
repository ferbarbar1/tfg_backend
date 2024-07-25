from django_filters import rest_framework as filters
from .models import Rating
from .models import Appointment


class AppointmentFilter(filters.FilterSet):
    class Meta:
        model = Appointment
        fields = ["client", "worker", "service", "inform"]


class RatingFilter(filters.FilterSet):
    class Meta:
        model = Rating
        fields = ["appointment", "client"]
