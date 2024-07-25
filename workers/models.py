from django.db import models
from authentication.models import Worker


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
        return f"{self.date} : {self.start_time} - {self.end_time}"


class Inform(models.Model):
    medical_history = models.TextField(blank=True, max_length=255)
    diagnostic = models.TextField(blank=True, max_length=255)
    treatment = models.TextField(blank=True, max_length=255)
