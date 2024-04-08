from rest_framework import routers
from .api import RatingViewSet

router = routers.DefaultRouter()

router.register("api/ratings", RatingViewSet, "ratings")

urlpatterns = router.urls
