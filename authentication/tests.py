from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import CustomUser, Owner, Worker, Client
from .serializers import CustomUserSerializer


class CustomUserModelTest(TestCase):
    def test_create_custom_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_create_owner(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owneruser", email="owner@example.com", password="password123"
        )
        owner = Owner.objects.create(user=user)
        self.assertEqual(owner.user.username, "owneruser")

    def test_create_worker(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="workeruser", email="worker@example.com", password="password123"
        )
        worker = Worker.objects.create(
            user=user, specialty="Physiotherapy", experience=5
        )
        self.assertEqual(worker.user.username, "workeruser")
        self.assertEqual(worker.specialty, "Physiotherapy")
        self.assertEqual(worker.experience, 5)

    def test_create_client(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="clientuser", email="client@example.com", password="password123"
        )
        client = Client.objects.create(user=user)
        self.assertEqual(client.user.username, "clientuser")


class CustomUserSerializerTest(TestCase):
    def test_serializer_with_valid_data(self):
        user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        serializer = CustomUserSerializer(user)
        self.assertEqual(serializer.data["username"], "testuser")
        self.assertEqual(serializer.data["email"], "test@example.com")

    def test_serializer_with_invalid_date_of_birth(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "date_of_birth": "2100-01-01",
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)


class UserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

    def test_register_client(self):
        url = reverse("register", kwargs={"user_type": "client"})
        data = {
            "user": {
                "username": "clientuser",
                "email": "client@example.com",
                "password": "password123",
                "first_name": "Client",
                "last_name": "User",
                "date_of_birth": "1990-01-01",
            }
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_login_client(self):
        client_user = CustomUser.objects.create_user(
            username="clientuser", email="client@example.com", password="password123"
        )
        Client.objects.create(user=client_user)
        url = reverse("login", kwargs={"user_type": "client"})
        data = {"username": "clientuser", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("change_password")
        data = {"new_password1": "newpassword123", "new_password2": "newpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_password_reset_request(self):
        url = reverse("password_reset_request")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_password_reset_confirm(self):
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        data = {"new_password1": "newpassword123", "new_password2": "newpassword123"}
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password("newpassword123"))
