from django.db import models
from django.db import models
from authentication.models import Worker
from django.utils import timezone
from django.core.exceptions import ValidationError


class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    workers = models.ManyToManyField(Worker, related_name="services")
    image = models.ImageField(upload_to="service_images/", blank=True, null=True)

    def __str__(self):
        return self.name

    def get_active_offers(self):
        active_offers = self.offers.filter(
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        )
        return active_offers

    def get_discounted_price(self):
        offers = self.get_active_offers()
        discounted_price = self.price
        for offer in offers:
            discounted_price *= 1 - offer.discount / 100
        return discounted_price

    def clean(self):
        if self.price <= 0:
            raise ValidationError("The price must be greater than zero.")
        if not self.name.strip():
            raise ValidationError("The name cannot be empty.")


class Offer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    services = models.ManyToManyField(Service, related_name="offers")

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("The start date must be before the end date.")
        if self.start_date <= timezone.now():
            raise ValidationError(
                "The start date must be after the current date and time."
            )
        if not (0 <= self.discount <= 100):
            raise ValidationError("The discount must be between 0 and 100.")


class Invoice(models.Model):
    appointment = models.OneToOneField(
        "clients.Appointment", on_delete=models.CASCADE, related_name="invoice"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.appointment.id}"

    @property
    def client_email(self):
        return self.appointment.client.user.email

    @property
    def service_name(self):
        return self.appointment.service.name

    @property
    def amount(self):
        return self.appointment.service.price

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("The amount must be greater than zero.")
