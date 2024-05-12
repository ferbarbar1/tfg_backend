from django.urls import path
from rest_framework import routers
from .views import CreateCheckoutSessionView
from .api import RatingViewSet

router = routers.DefaultRouter()

router.register("api/ratings", RatingViewSet, "ratings")

urlpatterns = [
    path(
        "api/payments/checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
]

urlpatterns += router.urls
