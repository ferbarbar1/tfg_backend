from django_filters import rest_framework as filters
from .models import Rating


class RatingFilter(filters.FilterSet):
    class Meta:
        model = Rating
        fields = ["service"]
