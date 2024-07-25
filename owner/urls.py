from rest_framework import routers
from .api import ServiceViewSet

router = routers.DefaultRouter()

router.register("api/services", ServiceViewSet, "services")

urlpatterns = router.urls
