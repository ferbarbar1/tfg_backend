from django.urls import path
from rest_framework import routers
from .api import ScheduleViewSet

router = routers.DefaultRouter()

router.register("api/schedules", ScheduleViewSet, "schedules")

urlpatterns = router.urls
