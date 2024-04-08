from .models import CustomUser, Owner, Worker, Client
from .serializers import (
    CustomUserSerializer,
    OwnerSerializer,
    WorkerSerializer,
    ClientSerializer,
)
from rest_framework import viewsets, permissions


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomUserSerializer


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = OwnerSerializer


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = WorkerSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientSerializer
