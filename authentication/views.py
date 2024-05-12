from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import OwnerSerializer, WorkerSerializer, ClientSerializer
from .models import CustomUser, Owner, Client, Worker


# Create your views here.
@api_view(["POST"])
def register(request, user_type):
    if user_type == "client":
        serializer_class = ClientSerializer
    elif user_type == "worker":
        serializer_class = WorkerSerializer
    elif user_type == "owner":
        serializer_class = OwnerSerializer
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
    if user_type not in ["client", "worker", "owner"]:
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
    elif user_type == "owner":
        owner = get_object_or_404(Owner, user=user)
        serializer = OwnerSerializer(instance=owner)

    return Response(
        {"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    role = user.get_role()

    if role == "owner":
        serializer = OwnerSerializer(instance=user.owner)
    elif role == "worker":
        serializer = WorkerSerializer(instance=user.worker)
    elif role == "client":
        serializer = ClientSerializer(instance=user.client)
    else:
        return Response(
            {"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(serializer.data, status=status.HTTP_200_OK)
