from rest_framework import serializers
from .models import Service, Offer
from authentication.serializers import WorkerSerializer


class ServiceSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = "__all__"


class OfferSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True
    )

    class Meta:
        model = Offer
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["services"] = ServiceSerializer(
            instance.services.all(), many=True
        ).data
        return representation
