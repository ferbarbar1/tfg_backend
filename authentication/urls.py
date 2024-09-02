from rest_framework import routers
from django.urls import path
from .views import (
    register,
    login,
    profile,
    change_password,
    password_reset_request,
    password_reset_confirm,
)
from .api import CustomUserViewSet, OwnerViewSet, WorkerViewSet, ClientViewSet

urlpatterns = [
    path("api/register/<str:user_type>/", register, name="register"),
    path("api/login/<str:user_type>/", login, name="login"),
    path("api/profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("password-reset/", password_reset_request, name="password_reset_request"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        password_reset_confirm,
        name="password_reset_confirm",
    ),
]

router = routers.DefaultRouter()

router.register("api/users", CustomUserViewSet, "users")
router.register("api/owners", OwnerViewSet, "owners")
router.register("api/workers", WorkerViewSet, "workers")
router.register("api/clients", ClientViewSet, "clients")

urlpatterns += router.urls
