from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from authentication.models import Client, Worker
from owner.models import Service
from workers.models import Inform


# Create your models here.
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    MODALITY_CHOICES = [
        ("VIRTUAL", "Virtual"),
        ("IN_PERSON", "In person"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_appointments"
    )
    worker = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="worker_appointments"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="service_appointments"
    )
    schedule = models.ForeignKey(
        "workers.Schedule",
        on_delete=models.CASCADE,
        related_name="schedule_appointment",
    )
    description = models.TextField(blank=True, max_length=255)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="CONFIRMED"
    )
    modality = models.CharField(
        max_length=10, choices=MODALITY_CHOICES, default="IN_PERSON"
    )
    inform = models.OneToOneField(
        Inform,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="appointment_inform",
    )
    # Campo para devolver el dinero en caso de cancelación
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    # Campos para las videollamadas
    client_peer_id = models.CharField(max_length=100, blank=True, null=True)
    worker_peer_id = models.CharField(max_length=100, blank=True, null=True)


class Rating(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_ratings"
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="appointment_ratings"
    )
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opinion = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)


class MedicalHistory(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_medical_history"
    )
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=255)
    medical_report = models.FileField(
        upload_to="medical_reports/", null=True, blank=True
    )
