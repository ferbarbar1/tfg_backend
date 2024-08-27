from rest_framework import routers
from .api import ServiceViewSet, OfferViewSet, InvoiceViewSet

router = routers.DefaultRouter()

router.register("api/services", ServiceViewSet, "services")
router.register("api/offers", OfferViewSet, "offers")
router.register("api/invoices", InvoiceViewSet, "invoices")

urlpatterns = router.urls
