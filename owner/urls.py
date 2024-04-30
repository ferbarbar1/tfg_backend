from rest_framework import routers
from django.urls import path
from .api import AppointmentViewSet, ServiceViewSet
from .views import CreateAppointmentView

router = routers.DefaultRouter()

router.register("api/appointments", AppointmentViewSet, "appointments")
router.register("api/services", ServiceViewSet, "services")

urlpatterns = [
    path(
        "api/appointments/create",
        CreateAppointmentView.as_view(),
        name="create_appointment",
    ),
]

urlpatterns += router.urls
