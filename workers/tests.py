from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from authentication.models import Worker, CustomUser
from .models import Schedule, Inform, Resource


class ScheduleModelTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create(
            user=CustomUser.objects.create_user(
                username="workeruser",
                email="worker@example.com",
                password="password123",
            ),
            specialty="Physiotherapy",
            experience=5,
        )

    def test_create_schedule(self):
        schedule = Schedule.objects.create(
            worker=self.worker,
            date=timezone.now().date() + timezone.timedelta(days=1),
            start_time="09:00",
            end_time="10:00",
        )
        self.assertEqual(schedule.worker, self.worker)
        self.assertTrue(schedule.available)

    def test_schedule_time_validation(self):
        schedule = Schedule(
            worker=self.worker,
            date=timezone.now().date() + timezone.timedelta(days=1),
            start_time="10:00",
            end_time="09:00",
        )
        with self.assertRaises(ValidationError):
            schedule.clean()

    def test_schedule_date_validation(self):
        schedule = Schedule(
            worker=self.worker,
            date=timezone.now().date() - timezone.timedelta(days=1),
            start_time="09:00",
            end_time="10:00",
        )
        with self.assertRaises(ValidationError):
            schedule.clean()


class InformModelTest(TestCase):
    def test_create_inform(self):
        inform = Inform.objects.create(
            relevant_information="Relevant information",
            diagnostic="Diagnostic information",
            treatment="Treatment information",
        )
        self.assertEqual(inform.relevant_information, "Relevant information")
        self.assertEqual(inform.diagnostic, "Diagnostic information")
        self.assertEqual(inform.treatment, "Treatment information")


class ResourceModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="authoruser", email="author@example.com", password="password123"
        )

    def test_create_resource_file(self):
        resource = Resource.objects.create(
            author=self.user,
            title="Test Resource",
            description="Test Description",
            resource_type="FILE",
            file="path/to/file",
        )
        self.assertEqual(resource.author, self.user)
        self.assertEqual(resource.title, "Test Resource")
        self.assertEqual(resource.description, "Test Description")
        self.assertEqual(resource.resource_type, "FILE")
        self.assertEqual(resource.file, "path/to/file")

    def test_create_resource_url(self):
        resource = Resource.objects.create(
            author=self.user,
            title="Test Resource",
            description="Test Description",
            resource_type="URL",
            url="http://example.com",
        )
        self.assertEqual(resource.author, self.user)
        self.assertEqual(resource.title, "Test Resource")
        self.assertEqual(resource.description, "Test Description")
        self.assertEqual(resource.resource_type, "URL")
        self.assertEqual(resource.url, "http://example.com")

    def test_resource_file_validation(self):
        resource = Resource(
            author=self.user,
            title="Test Resource",
            description="Test Description",
            resource_type="FILE",
        )
        with self.assertRaises(ValidationError):
            resource.clean()

    def test_resource_url_validation(self):
        resource = Resource(
            author=self.user,
            title="Test Resource",
            description="Test Description",
            resource_type="URL",
        )
        with self.assertRaises(ValidationError):
            resource.clean()
