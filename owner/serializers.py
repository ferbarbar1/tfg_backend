from rest_framework import serializers
from .models import Service
from authentication.serializers import WorkerSerializer


class ServiceSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = "__all__"
