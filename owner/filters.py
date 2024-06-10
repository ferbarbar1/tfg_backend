from django_filters import rest_framework as filters
from workers.models import Appointment


class AppointmentFilter(filters.FilterSet):
    class Meta:
        model = Appointment
        fields = ["client", "worker", "service"]
