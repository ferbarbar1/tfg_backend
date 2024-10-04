from django.urls import path
from rest_framework import routers
from .views import CreateCheckoutSessionView, webhook, CancelAppointmentView
from .api import AppointmentViewSet, RatingViewSet, MedicalHistoryViewSet

router = routers.DefaultRouter()

router.register("api/appointments", AppointmentViewSet, "appointments")
router.register("api/ratings", RatingViewSet, "ratings")
router.register("api/medical-histories", MedicalHistoryViewSet, "medical-histories")

urlpatterns = [
    path(
        "api/payments/checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("api/webhook/", webhook, name="webhook"),
    path(
        "api/appointments/cancel/",
        CancelAppointmentView.as_view(),
        name="cancel-appointment",
    ),
]

urlpatterns += router.urls
