from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from authentication.models import Worker
from .models import Service, Offer, Invoice
from clients.models import Appointment, Client
from django.contrib.auth import get_user_model
from workers.models import Schedule


class ServiceModelTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create(
            user=get_user_model().objects.create_user(
                username="workeruser",
                email="worker@example.com",
                password="password123",
            ),
            specialty="Physiotherapy",
            experience=5,
        )

    def test_create_service(self):
        service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            price=100.00,
        )
        service.workers.add(self.worker)
        self.assertEqual(service.name, "Test Service")
        self.assertEqual(service.description, "Test Description")
        self.assertEqual(service.price, 100.00)
        self.assertIn(self.worker, service.workers.all())

    def test_service_price_validation(self):
        service = Service(
            name="Test Service",
            description="Test Description",
            price=-10.00,
        )
        with self.assertRaises(ValidationError):
            service.clean()

    def test_service_name_validation(self):
        service = Service(
            name="",
            description="Test Description",
            price=100.00,
        )
        with self.assertRaises(ValidationError):
            service.clean()

    def test_get_discounted_price(self):
        service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            price=100.00,
        )
        offer = Offer.objects.create(
            name="Test Offer",
            description="Test Offer Description",
            discount=10.00,
            start_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
        )
        service.offers.add(offer)
        discounted_price = service.price
        for offer in service.offers.all():
            discounted_price *= 1 - float(offer.discount) / 100
        self.assertEqual(discounted_price, 90.00)


class OfferModelTest(TestCase):
    def test_create_offer(self):
        service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            price=100.00,
        )
        offer = Offer.objects.create(
            name="Test Offer",
            description="Test Offer Description",
            discount=10.00,
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
        )
        offer.services.add(service)
        self.assertEqual(offer.name, "Test Offer")
        self.assertEqual(offer.description, "Test Offer Description")
        self.assertEqual(offer.discount, 10.00)
        self.assertIn(service, offer.services.all())

    def test_offer_date_validation(self):
        offer = Offer(
            name="Test Offer",
            description="Test Offer Description",
            discount=10.00,
            start_date=timezone.now() + timezone.timedelta(days=2),
            end_date=timezone.now() + timezone.timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            offer.clean()

    def test_offer_discount_validation(self):
        offer = Offer(
            name="Test Offer",
            description="Test Offer Description",
            discount=110.00,
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
        )
        with self.assertRaises(ValidationError):
            offer.clean()


class InvoiceModelTest(TestCase):
    def setUp(self):
        self.client_user = get_user_model().objects.create_user(
            username="clientuser", email="client@example.com", password="password123"
        )
        self.client = Client.objects.create(user=self.client_user)
        self.worker = Worker.objects.create(
            user=get_user_model().objects.create_user(
                username="workeruser",
                email="worker@example.com",
                password="password123",
            ),
            specialty="Physiotherapy",
            experience=5,
        )
        self.service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            price=100.00,
        )
        self.schedule = Schedule.objects.create(
            worker=self.worker,
            start_time="09:00",
            end_time="10:00",
            date=timezone.now().date() + timezone.timedelta(days=1),
        )
        self.appointment = Appointment.objects.create(
            client=self.client,
            worker=self.worker,
            service=self.service,
            schedule=self.schedule,
            description="Test Appointment",
            status="CONFIRMED",
            stripe_session_id="cs_test_123",
        )

    def test_create_invoice(self):
        invoice = Invoice.objects.create(appointment=self.appointment)
        self.assertEqual(invoice.appointment, self.appointment)
        self.assertEqual(invoice.client_email, self.client_user.email)
        self.assertEqual(invoice.service_name, self.service.name)
        self.assertEqual(invoice.amount, self.service.price)

    def test_invoice_amount_validation(self):
        self.service.price = -100.00
        self.service.save()
        invoice = Invoice(appointment=self.appointment)
        with self.assertRaises(ValidationError):
            invoice.clean()
