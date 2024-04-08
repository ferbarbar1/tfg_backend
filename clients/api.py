from .models import Rating
from .serializers import RatingSerializer
from rest_framework import viewsets, permissions


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RatingSerializer
