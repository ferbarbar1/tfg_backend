from django.db import models
from django.db import models
from authentication.models import Worker


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    workers = models.ManyToManyField(Worker, related_name="services")

    def __str__(self):
        return self.name
