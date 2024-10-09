from django.db import models
from authentication.models import Worker, CustomUser
from django.core.exceptions import ValidationError
from django.utils import timezone


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

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start time must be before the end time.")
        if self.date < timezone.now().date():
            raise ValidationError("The date cannot be in the past.")


class Inform(models.Model):
    relevant_information = models.TextField(null=True, max_length=255)
    diagnostic = models.TextField(max_length=255)
    treatment = models.TextField(max_length=255)


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("FILE", "File"),
        ("URL", "URL"),
    ]

    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="resources"
    )
    image_preview = models.ImageField(
        upload_to="resources_images/", null=True, blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=500)
    resource_type = models.CharField(
        max_length=10, choices=RESOURCE_TYPE_CHOICES, default="OTHER"
    )
    file = models.FileField(upload_to="resources_files/", null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.resource_type == "FILE" and not self.file:
            raise ValidationError("A file must be provided for resource type 'FILE'.")
        if self.resource_type == "URL" and not self.url:
            raise ValidationError("A URL must be provided for resource type 'URL'.")
