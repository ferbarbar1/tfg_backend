from rest_framework import serializers
from .models import Rating
from authentication.serializers import ClientSerializer, WorkerSerializer


class RatingSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = "__all__"
