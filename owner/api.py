from .models import Service, Offer
from .serializers import ServiceSerializer, OfferSerializer
from rest_framework import viewsets, permissions


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ServiceSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = OfferSerializer
