from django_filters import rest_framework as filters
from .models import CustomUser


class CustomUserFilter(filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = ["id", "username"]
