from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import OwnerSerializer, WorkerSerializer, ClientSerializer
from .models import CustomUser, Owner, Client, Worker
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_exempt


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


# Vista para usuarios autenticados que quieren cambiar su contraseña
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    form = SetPasswordForm(user, request.data)
    if form.is_valid():
        form.save()
        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


# Vista para usuarios no autenticados que quieren cambiar su contraseña
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    form = PasswordResetForm(request.data)
    if form.is_valid():
        data = form.cleaned_data["email"]
        associated_users = CustomUser.objects.filter(email=data)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                reset_link = f"http://localhost:5173/reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}"
                message = f"""
                Hola {user.get_full_name()},

                Recibimos una solicitud para restablecer tu contraseña en FisioterAppIA Clinic.

                Para restablecer tu contraseña, haz clic en el siguiente enlace o pégalo en tu navegador:
                {reset_link}

                Si no solicitaste un restablecimiento de contraseña, puedes ignorar este correo electrónico.

                Gracias,
                El equipo de FisioterAppIA Clinic
                """
                send_mail(
                    subject,
                    message,
                    "fisioterappia.clinic@gmail.com",
                    [user.email],
                    fail_silently=False,
                )
        return Response(
            {"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK
        )
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


# Vista para confirmar el reset de contraseña
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        form = SetPasswordForm(user, request.data)
        if form.is_valid():
            form.save()
            return Response(
                {"detail": "Password has been reset."}, status=status.HTTP_200_OK
            )
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
