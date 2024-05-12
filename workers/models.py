from django.db import models
from authentication.models import Client, Worker


# Create your models here.
class Schedule(models.Model):
    worker = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="schedules"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.worker}: {self.start_time} - {self.end_time}"


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
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="appointments"
    )
    description = models.TextField(blank=True, max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    modality = models.CharField(
        max_length=10, choices=MODALITY_CHOICES, default="IN_PERSON"
    )
    meeting_link = models.URLField(blank=True, null=True)
