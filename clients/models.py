from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import Client, Worker
from owner.models import Service


# Create your models here.
class Rating(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_ratings"
    )
    worker = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="worker_ratings"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="service_ratings"
    )
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opinion = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "worker", "service")
