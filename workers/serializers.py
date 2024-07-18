from rest_framework import serializers
from .models import Schedule, Inform


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class InformSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(InformSerializer, self).__init__(*args, **kwargs)
        from clients.serializers import AppointmentSerializer

        self.fields["appointment"] = AppointmentSerializer(read_only=True)

    class Meta:
        model = Inform
        fields = "__all__"
