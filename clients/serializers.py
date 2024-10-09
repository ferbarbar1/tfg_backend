from rest_framework import serializers
from .models import Rating, Appointment, MedicalHistory
from owner.models import Service
from workers.models import Schedule, Inform
from authentication.models import Client
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from authentication.serializers import WorkerSerializer, ClientSerializer
from workers.serializers import ScheduleSerializer, InformSerializer
from owner.serializers import ServiceSerializer
from datetime import timedelta, datetime


class AppointmentSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    inform = InformSerializer(read_only=True)

    # Campos para peer_ids
    client_peer_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    worker_peer_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # Campos para escritura
    schedule_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Schedule.objects.all(),
        source="schedule",
        required=False,
    )
    client_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Client.objects.all(), source="client", required=False
    )
    service_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Service.objects.all(),
        source="service",
        required=False,
    )
    inform_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Inform.objects.all(), source="inform", required=False
    )
    stripe_session_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Appointment
        fields = "__all__"

    def validate_status(self, value):
        if value not in dict(Appointment.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status")
        return value

    def validate_modality(self, value):
        if value not in dict(Appointment.MODALITY_CHOICES):
            raise serializers.ValidationError("Invalid modality")
        return value

    def validate(self, attrs):
        schedule = attrs.get("schedule")
        if schedule:
            if schedule.date < datetime.now().date():
                raise serializers.ValidationError(
                    "The appointment date must be in the future."
                )
            if (
                schedule.date == datetime.now().date()
                and schedule.start_time < (datetime.now() + timedelta(hours=24)).time()
            ):
                raise serializers.ValidationError(
                    "Appointments must be booked at least 24 hours in advance."
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        service = validated_data.get("service")
        schedule = validated_data.get("schedule")
        if not service:
            raise serializers.ValidationError("Service is required.")
        try:
            worker = self.find_eligible_worker(service.id, schedule.date)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Service not found.")

        if worker is None:
            raise serializers.ValidationError(
                "No available workers for the selected service and schedule. "
            )

        validated_data["worker"] = worker
        appointment = Appointment.objects.create(**validated_data)
        schedule.available = False
        schedule.save()
        return appointment

    def find_eligible_worker(self, service_id, date):
        service = Service.objects.get(id=service_id)
        workers_offering_service = service.workers.all()

        for worker in workers_offering_service:
            if not self.is_daily_limit_reached(
                worker.id, date
            ) and not self.is_weekly_limit_reached(worker.id, date):
                return worker
        return None

    def is_daily_limit_reached(self, worker_id, date):
        appointments_same_day = Appointment.objects.filter(
            worker__id=worker_id, schedule__date=date
        ).count()
        return appointments_same_day >= 8

    def is_weekly_limit_reached(self, worker_id, date):
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        appointments_same_week = Appointment.objects.filter(
            worker__id=worker_id, schedule__date__range=[week_start, week_end]
        )
        total_hours = appointments_same_week.aggregate(
            total_hours=ExpressionWrapper(
                Sum(F("schedule__end_time") - F("schedule__start_time")),
                output_field=fields.DurationField(),
            )
        )["total_hours"]
        return total_hours is not None and total_hours.total_seconds() / 3600 > 40

    @transaction.atomic
    def update(self, instance, validated_data):
        # Actualiza campos modificables directamente
        instance.client = validated_data.get("client", instance.client)
        instance.service = validated_data.get("service", instance.service)
        instance.status = validated_data.get("status", instance.status)

        # Actualiza el campo inform si está presente en los datos validados
        new_inform = validated_data.get("inform")
        if new_inform:
            instance.inform = new_inform

        # Actualiza los campos de peer_id si están presentes
        instance.client_peer_id = validated_data.get(
            "client_peer_id", instance.client_peer_id
        )
        instance.worker_peer_id = validated_data.get(
            "worker_peer_id", instance.worker_peer_id
        )

        # Si se proporciona un nuevo schedule, actualiza el horario de la cita
        new_schedule = validated_data.get("schedule")
        if new_schedule and new_schedule != instance.schedule:
            # Marca el horario anterior como disponible
            old_schedule = instance.schedule
            old_schedule.available = True
            old_schedule.save()

            # Verifica si el nuevo horario está disponible
            if not new_schedule.available:
                raise serializers.ValidationError("This schedule is not available.")

            # Asigna el nuevo horario y marca como no disponible
            instance.schedule = new_schedule
            new_schedule.available = False
            new_schedule.save()

            # Reasigna un trabajador si es necesario
            worker = self.find_eligible_worker(instance.service.id, new_schedule.date)
            if worker is None:
                raise serializers.ValidationError(
                    "No available workers for the selected service and schedule."
                )
            instance.worker = worker

        # Guarda la instancia después de todas las actualizaciones
        instance.save()
        return instance


class RatingSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), write_only=True, source="client"
    )
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), write_only=True, source="appointment"
    )

    class Meta:
        model = Rating
        fields = [
            "id",
            "client",
            "client_id",
            "rate",
            "opinion",
            "date",
            "appointment",
            "appointment_id",
        ]

    def validate(self, data):
        if data["rate"] < 1 or data["rate"] > 5:
            raise serializers.ValidationError("Rate must be between 1 and 5")
        if not data["opinion"]:
            raise serializers.ValidationError("Opinion is required")
        return data


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = "__all__"
