from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from datetime import date


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def get_role(self):
        if hasattr(self, "owner"):
            return "owner"
        elif hasattr(self, "worker"):
            return "worker"
        elif hasattr(self, "client"):
            return "client"
        else:
            return None


class Owner(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Asignar todos los permisos a Owner
        permissions = Permission.objects.all()
        for permission in permissions:
            if not self.user.user_permissions.filter(id=permission.id).exists():
                self.user.user_permissions.add(permission)

    class Meta:
        verbose_name = "Owner"
        verbose_name_plural = "Owners"


class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=8, decimal_places=2)
    specialty = models.CharField(max_length=255)
    experience = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"


class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    SUBCRIPTION_PLANS = [
        ("FREE", "free"),
        ("PREMIUM", "premium"),
    ]
    subscription_plan = models.CharField(
        max_length=10, choices=SUBCRIPTION_PLANS, default="FREE"
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
