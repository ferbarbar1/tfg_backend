from django.urls import path
from rest_framework import routers
from .api import ScheduleViewSet
from .views import CreateAppointmentView

router = routers.DefaultRouter()

router.register("api/schedules", ScheduleViewSet, "schedules")

# Agrega la URL para la vista CreateAppointmentView
urlpatterns = [
    path(
        "api/appointments/create",
        CreateAppointmentView.as_view(),
        name="create_appointment",
    ),
] + router.urls
