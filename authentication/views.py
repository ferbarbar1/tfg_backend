from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import ClientSerializer, WorkerSerializer
from .models import CustomUser, Client, Worker


# Create your views here.
"""
@api_view(["POST"])
def register(request, user_type):
    if user_type == "client":
        serializer_class = ClientSerializer
    elif user_type == "worker":
        serializer_class = WorkerSerializer
    else:
        return Response(
            {"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = serializer_class(data=request.data)
    if serializer.is_valid():
        serializer.save()

        user = serializer_class.Meta.model.objects.get(
            username=serializer.data["username"]
        )
        user.set_password(serializer.data["password"])
        user.save()

        token = Token.objects.create(user=user)
        return Response(
            {"token": token.key, "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""


@api_view(["POST"])
def register(request, user_type):
    if user_type == "client":
        serializer_class = ClientSerializer
    elif user_type == "worker":
        serializer_class = WorkerSerializer
    else:
        return Response(
            {"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = serializer_class(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        token = Token.objects.create(user=user.user)
        return Response(
            {"token": token.key, "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request, user_type):
    if user_type not in ["client", "worker"]:
        return Response(
            {"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = get_object_or_404(CustomUser, username=request.data["username"])
    if not user.check_password(request.data["password"]):
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )

    token, created = Token.objects.get_or_create(user=user)
    if user_type == "client":
        client = get_object_or_404(Client, user=user)
        serializer = ClientSerializer(instance=client)
    elif user_type == "worker":
        worker = get_object_or_404(Worker, user=user)
        serializer = WorkerSerializer(instance=worker)

    return Response(
        {"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK
    )


"""
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(instance=request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
"""
