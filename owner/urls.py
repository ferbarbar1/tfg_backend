from rest_framework import routers
from .api import ServiceViewSet, OfferViewSet

router = routers.DefaultRouter()

router.register("api/services", ServiceViewSet, "services")
router.register("api/offers", OfferViewSet, "offers")

urlpatterns = router.urls
