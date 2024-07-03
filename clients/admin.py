from django.contrib import admin
from .models import Rating, Appointment

# Register your models here.
admin.site.register(Appointment)
admin.site.register(Rating)
