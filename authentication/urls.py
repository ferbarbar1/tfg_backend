from rest_framework import routers
from django.urls import path
from .views import register, login, profile
from .api import CustomUserViewSet, OwnerViewSet, WorkerViewSet, ClientViewSet

urlpatterns = [
    path("api/register/<str:user_type>/", register, name="register"),
    path("api/login/<str:user_type>/", login, name="login"),
    path("api/profile/", profile, name="profile"),
]

router = routers.DefaultRouter()

router.register("api/users", CustomUserViewSet, "users")
router.register("api/owners", OwnerViewSet, "owners")
router.register("api/workers", WorkerViewSet, "workers")
router.register("api/clients", ClientViewSet, "clients")

urlpatterns += router.urls
