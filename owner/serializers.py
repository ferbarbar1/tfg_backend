from rest_framework import serializers
from .models import Service, Offer, Invoice
from authentication.serializers import WorkerSerializer
from django.utils import timezone


class ServiceSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many=True, read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = "__all__"

    def get_discounted_price(self, obj):
        discounted_price = obj.get_discounted_price()
        if discounted_price != obj.price:
            return discounted_price
        return None

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("The price must be greater than zero.")
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("The name cannot be empty.")
        return value


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

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "The start date must be before the end date."
            )
        if data["start_date"] <= timezone.now():
            raise serializers.ValidationError(
                "The start date must be after the current date and time."
            )
        if not (0 <= data["discount"] <= 100):
            raise serializers.ValidationError("The discount must be between 0 and 100.")
        return data


class InvoiceSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField()
    amount = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = ["id", "appointment", "created_at", "service_name", "amount"]

    def validate_appointment(self, value):
        if not value:
            raise serializers.ValidationError(
                "The associated appointment must exist and be valid."
            )
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The amount must be greater than zero.")
        return value
