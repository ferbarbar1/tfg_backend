from rest_framework import routers
from .api import ConversationViewSet, MessageViewSet, NotificationViewSet

router = routers.DefaultRouter()

router.register("api/conversations", ConversationViewSet, "conversations")
router.register("api/messages", MessageViewSet, "messages")
router.register("api/notifications", NotificationViewSet, "notifications")

urlpatterns = router.urls
