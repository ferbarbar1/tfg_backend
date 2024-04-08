from rest_framework import routers
from .api import AppointmentViewSet, ServiceViewSet

router = routers.DefaultRouter()

router.register("api/appointments", AppointmentViewSet, "appointments")
router.register("api/services", ServiceViewSet, "services")

urlpatterns = router.urls
