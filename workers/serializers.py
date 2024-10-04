from rest_framework import serializers
from .models import Schedule, Inform, Resource
from authentication.models import CustomUser
from authentication.serializers import CustomUserSerializer
from django.utils import timezone


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "The start time must be before the end time."
            )
        if data["date"] < timezone.now().date():
            raise serializers.ValidationError("The date cannot be in the past.")
        return data


class InformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inform
        fields = "__all__"


class ResourceSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Resource
        fields = "__all__"

    def to_representation(self, instance):
        # En el modo de lectura, usa el CustomUserSerializer
        self.fields["author"] = CustomUserSerializer()
        return super(ResourceSerializer, self).to_representation(instance)

    def validate(self, data):
        if data.get("resource_type") == "FILE" and not data.get("file"):
            raise serializers.ValidationError(
                "A file must be provided for resource type 'FILE'."
            )
        if data.get("resource_type") == "URL" and not data.get("url"):
            raise serializers.ValidationError(
                "A URL must be provided for resource type 'URL'."
            )
        return data
