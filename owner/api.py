from .models import Service, Offer, Invoice
from .serializers import ServiceSerializer, OfferSerializer, InvoiceSerializer
from rest_framework import viewsets, permissions


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ServiceSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = OfferSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = InvoiceSerializer
