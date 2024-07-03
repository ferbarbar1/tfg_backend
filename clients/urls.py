from django.urls import path
from rest_framework import routers
from .views import CreateCheckoutSessionView, webhook, ZoomAuthView, ZoomCallbackView
from .api import AppointmentViewSet, RatingViewSet

router = routers.DefaultRouter()

router.register("api/appointments", AppointmentViewSet, "appointments")
router.register("api/ratings", RatingViewSet, "ratings")

urlpatterns = [
    path(
        "api/payments/checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("api/webhook/", webhook, name="webhook"),
    path("api/zoom/auth/", ZoomAuthView.as_view(), name="zoom_auth"),
    path("api/oauth/callback/", ZoomCallbackView.as_view(), name="zoom_callback"),
]

urlpatterns += router.urls
