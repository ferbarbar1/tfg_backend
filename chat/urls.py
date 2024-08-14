from rest_framework import routers
from .api import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()

router.register("api/conversations", ConversationViewSet, "conversations")
router.register("api/messages", MessageViewSet, "messages")

urlpatterns = router.urls
