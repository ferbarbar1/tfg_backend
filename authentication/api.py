from .models import CustomUser, Owner, Worker, Client
from .serializers import (
    CustomUserSerializer,
    OwnerSerializer,
    WorkerSerializer,
    ClientSerializer,
)
from .filters import CustomUserFilter, OwnerFilter, WorkerFilter, ClientFilter
from rest_framework import viewsets, permissions


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomUserSerializer
    filterset_class = CustomUserFilter


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = OwnerSerializer
    filterset_class = OwnerFilter


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = WorkerSerializer
    filterset_class = WorkerFilter


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientSerializer
    filterset_class = ClientFilter
