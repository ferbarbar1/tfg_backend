from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import Client, Worker
from owner.models import Service


# Create your models here.
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
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
        Service, on_delete=models.CASCADE, related_name="appointments"
    )
    schedule = models.ForeignKey(
        "workers.Schedule", on_delete=models.CASCADE, related_name="appointments"
    )
    description = models.TextField(blank=True, max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    modality = models.CharField(
        max_length=10, choices=MODALITY_CHOICES, default="IN_PERSON"
    )
    meeting_link = models.URLField(blank=True, null=True)


class Rating(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_ratings"
    )
    # worker = models.ForeignKey(
    #     Worker, on_delete=models.CASCADE, related_name="worker_ratings", null=True
    # )
    # service = models.ForeignKey(
    #     Service, on_delete=models.CASCADE, related_name="service_ratings"
    # )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="appointment_ratings"
    )
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opinion = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
