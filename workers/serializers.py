from rest_framework import serializers
from .models import Schedule, Inform


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class InformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inform
        fields = "__all__"
