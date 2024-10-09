from django_filters import rest_framework as filters
from .models import CustomUser, Owner, Worker, Client


class CustomUserFilter(filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = ["id", "username"]


class OwnerFilter(filters.FilterSet):
    class Meta:
        model = Owner
        fields = ["id"]


class WorkerFilter(filters.FilterSet):
    class Meta:
        model = Worker
        fields = ["id"]


class ClientFilter(filters.FilterSet):
    class Meta:
        model = Client
        fields = ["id"]
