from django.urls import path
from rest_framework import routers
from .api import ScheduleViewSet, InformViewSet

router = routers.DefaultRouter()

router.register("api/schedules", ScheduleViewSet, "schedules")
router.register("api/informs", InformViewSet, "informs")

urlpatterns = router.urls
