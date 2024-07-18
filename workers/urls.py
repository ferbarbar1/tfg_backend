from django.urls import path
from rest_framework import routers
from .api import ScheduleViewSet, InformViewSet
from .views import ZoomAuthView, ZoomCallbackView, CreateZoomMeetingView

router = routers.DefaultRouter()

router.register("api/schedules", ScheduleViewSet, "schedules")
router.register("api/informs", InformViewSet, "informs")

urlpatterns = [
    path("api/zoom/auth/", ZoomAuthView.as_view(), name="zoom_auth"),
    path("api/oauth/callback/", ZoomCallbackView.as_view(), name="zoom_callback"),
    path(
        "api/appointments/<int:appointment_id>/create_zoom_meeting/",
        CreateZoomMeetingView.as_view(),
        name="create_zoom_meeting",
    ),
]

urlpatterns += router.urls
