from rest_framework import serializers
from workers.models import Appointment
from .models import Service
from workers.serializers import ScheduleSerializer
from workers.models import Schedule
from authentication.serializers import WorkerSerializer, ClientSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer()
    worker = WorkerSerializer()
    client = ClientSerializer()

    class Meta:
        model = Appointment
        fields = "__all__"

    def create(self, validated_data):
        schedule_data = validated_data.pop("schedule")
        schedule = Schedule.objects.create(**schedule_data)
        appointment = Appointment.objects.create(schedule=schedule, **validated_data)
        return appointment

    def update(self, instance, validated_data):
        schedule_data = validated_data.pop("schedule")
        schedule = instance.schedule

        # Actualiza los campos del horario
        schedule.date = schedule_data.get("date", schedule.date)
        schedule.start_time = schedule_data.get("start_time", schedule.start_time)
        schedule.end_time = schedule_data.get("end_time", schedule.end_time)
        schedule.save()

        # Actualiza los campos de la cita
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class ServiceSerializer(serializers.ModelSerializer):
    workers = WorkerSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = "__all__"
