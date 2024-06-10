from rest_framework import serializers
from .models import Rating
from authentication.serializers import ClientSerializer


class RatingSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Rating
        fields = ["id", "client", "rate", "opinion", "date", "appointment"]
