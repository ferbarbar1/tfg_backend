from django.db import models
from django.db import models
from authentication.models import Worker
from django.utils import timezone


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    workers = models.ManyToManyField(Worker, related_name="services")
    image = models.ImageField(upload_to="service_images/", blank=True, null=True)

    def __str__(self):
        return self.name

    def get_active_offer(self):
        active_offer = self.offers.filter(
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        ).first()
        return active_offer

    def get_discounted_price(self):
        offer = self.get_active_offer()
        if offer:
            return self.price * (1 - offer.discount / 100)
        return self.price


class Offer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    services = models.ManyToManyField(Service, related_name="offers")

    def __str__(self):
        return self.name
