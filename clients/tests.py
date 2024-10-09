from django.test import TestCase
from django.core.exceptions import ValidationError
from authentication.models import Client, Worker
from owner.models import Service
from workers.models import Inform, Schedule
from .models import Appointment, Rating, MedicalHistory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from unittest.mock import patch


class AppointmentModelTest(TestCase):
    def setUp(self):
        User = get_user_model()

        # Crear un cliente
        user_client = User.objects.create_user(
            username="clientuser", email="client@example.com", password="password123"
        )
        self.client = Client.objects.create(user=user_client)

        # Crear un trabajador
        user_worker = User.objects.create_user(
            username="workeruser", email="worker@example.com", password="password123"
        )
        self.worker = Worker.objects.create(
            user=user_worker, specialty="Physiotherapy", experience=5
        )

        # Crear un servicio
        self.service = Service.objects.create(
            name="Service 1", description="Service description", price=50.00
        )
        self.service.workers.add(self.worker)

        # Crear un informe
        self.inform = Inform.objects.create(
            relevant_information="Info", diagnostic="Diagnosis", treatment="Treatment"
        )

        self.schedule = Schedule.objects.create(
            worker=self.worker,
            start_time="09:00",
            end_time="10:00",
            date="2025-01-01",
        )

    def test_create_appointment(self):
        # Probar la creación de una cita
        appointment = Appointment.objects.create(
            client=self.client,
            worker=self.worker,
            service=self.service,
            schedule=self.schedule,
            description="Dolor de espalda",
            status="CONFIRMED",
            modality="IN_PERSON",
            inform=self.inform,
        )

        self.assertEqual(appointment.client, self.client)
        self.assertEqual(appointment.worker, self.worker)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.status, "CONFIRMED")
        self.assertEqual(appointment.modality, "IN_PERSON")
        self.assertEqual(appointment.inform, self.inform)

    def test_invalid_status_appointment(self):
        # Probar un status inválido
        with self.assertRaises(ValidationError):
            appointment = Appointment(
                client=self.client,
                worker=self.worker,
                service=self.service,
                schedule=self.schedule,
                description="Invalid status",
                status="INVALID_STATUS",  # Esto debería generar un error
            )
            appointment.full_clean()  # Dispara las validaciones de Django


class RatingModelTest(TestCase):
    def setUp(self):
        User = get_user_model()

        # Crear cliente y trabajador
        user_client = User.objects.create_user(
            username="clientuser", email="client@example.com", password="password123"
        )
        self.client = Client.objects.create(user=user_client)

        user_worker = User.objects.create_user(
            username="workeruser", email="worker@example.com", password="password123"
        )
        self.worker = Worker.objects.create(
            user=user_worker, specialty="Physiotherapy", experience=5
        )

        self.schedule = Schedule.objects.create(
            worker=self.worker,
            start_time="09:00",
            end_time="10:00",
            date="2025-01-01",
        )

        # Crear una cita
        self.service = Service.objects.create(
            name="Service 1", description="Service description", price=50.00
        )
        self.service.workers.add(self.worker)

        self.appointment = Appointment.objects.create(
            client=self.client,
            worker=self.worker,
            service=self.service,
            schedule=self.schedule,
            description="Test appointment",
            status="COMPLETED",
        )

    def test_create_rating(self):
        # Probar la creación de una valoración
        rating = Rating.objects.create(
            client=self.client,
            appointment=self.appointment,
            rate=4,
            opinion="Buen servicio",
        )
        self.assertEqual(rating.client, self.client)
        self.assertEqual(rating.appointment, self.appointment)
        self.assertEqual(rating.rate, 4)
        self.assertEqual(rating.opinion, "Buen servicio")

    def test_invalid_rate(self):
        # Probar un rate inválido
        with self.assertRaises(ValidationError):
            rating = Rating(
                client=self.client,
                appointment=self.appointment,
                rate=6,  # Valor inválido (mayor que 5)
                opinion="Excesivamente bueno",
            )
            rating.full_clean()


class MedicalHistoryModelTest(TestCase):
    def setUp(self):
        User = get_user_model()

        # Crear un cliente
        user_client = User.objects.create_user(
            username="clientuser", email="client@example.com", password="password123"
        )
        self.client = Client.objects.create(user=user_client)

    def test_create_medical_history(self):
        # Probar la creación de un historial médico
        medical_history = MedicalHistory.objects.create(
            client=self.client,
            title="Antecedentes médicos",
            description="Descripción de antecedentes",
        )
        self.assertEqual(medical_history.client, self.client)
        self.assertEqual(medical_history.title, "Antecedentes médicos")
        self.assertEqual(medical_history.description, "Descripción de antecedentes")
