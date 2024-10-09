from datetime import time, date, datetime, timedelta
from django.core.files import File
from faker import Faker
from django.utils import timezone
import os
import shutil
import sqlite3
import random
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.management import call_command
from authentication.models import CustomUser, Owner, Client, Worker
from workers.models import Schedule, Inform, Resource
from clients.models import Appointment, Rating, MedicalHistory
from owner.models import Service, Offer, Invoice
from chat.models import Conversation, Message, Notification

fake = Faker()


def remove_pycache_and_clean_migrations(root_path, modules):
    for module in modules:
        module_path = os.path.join(root_path, module)
        print(f"Revisando módulo: {module}")
        pycache_found = False
        migrations_cleaned = False

        for root, dirs, files in os.walk(module_path):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                shutil.rmtree(pycache_path)
                print(f"Eliminado: {pycache_path}")
                pycache_found = True

            if "migrations" in root:
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                        print(f"Eliminado: {file_path}")
                        migrations_cleaned = True

        if not pycache_found:
            print(f"No se encontró __pycache__ para eliminar en el módulo {module}.")
        if not migrations_cleaned:
            print(
                f"No se encontraron archivos en 'migrations' para eliminar en el módulo {module}."
            )


def clean_db():
    try:
        conn = sqlite3.connect("db.sqlite3")
        cur = conn.cursor()

        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'"
        )
        tables = cur.fetchall()
        print(f"Se encontraron {len(tables)} tablas.")

        for table in tables:
            print(f"Eliminando tabla: {table[0]}...")
            cur.execute(f"DROP TABLE {table[0]}")
            conn.commit()

        print("Todas las tablas han sido eliminadas.")

        cur.execute("DELETE FROM sqlite_sequence")
        conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def run_migrations():
    call_command("makemigrations")
    call_command("migrate")


def create_users():
    if not CustomUser.objects.filter(email="owner@example.com").exists():
        owner_user = CustomUser.objects.create_user(
            "owner",
            "owner@example.com",
            "ownerpass",
            first_name="Owner",
            last_name="User",
            date_of_birth=date(1980, 1, 1),
        )
        Owner.objects.create(user=owner_user)
        owner_user.get_role = "owner"
        owner_user.save()

    if not CustomUser.objects.filter(email="superuser@example.com").exists():
        super_user = CustomUser.objects.create_superuser(
            "superuser",
            "superuser@example.com",
            "superuser",
            first_name="Super",
            last_name="User",
            date_of_birth=date(1985, 5, 15),
        )
        super_user.get_role = "superuser"
        super_user.save()

    worker_images = ["worker0.png", "worker1.jpg", "worker2.png"]
    for i in range(3):  # Crear solo 3 trabajadores
        if not CustomUser.objects.filter(email=f"worker{i}@example.com").exists():
            worker_user = CustomUser.objects.create_user(
                f"worker{i}",
                f"worker{i}@example.com",
                "workerpass",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=60),
            )
            worker_image_path = f"media/profile_images/{random.choice(worker_images)}"
            with open(worker_image_path, "rb") as img_file:
                worker_user.image.save(
                    worker_images[i % len(worker_images)], File(img_file), save=True
                )
            Worker.objects.create(
                user=worker_user,
                specialty=fake.job(),
                experience=random.randint(1, 20),
            )
            worker_user.get_role = "worker"
            worker_user.save()

    for i in range(3):  # Crear solo 3 clientes
        if not CustomUser.objects.filter(email=f"client{i}@example.com").exists():
            client_user = CustomUser.objects.create_user(
                f"client{i}",
                f"client{i}@example.com",
                "clientpass",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            )
            Client.objects.create(user=client_user)
            client_user.get_role = "client"
            client_user.save()
    print("Usuarios creados con éxito")


def create_schedules():
    workers = Worker.objects.all()
    start_times_morning = [
        time(9, 0),
        time(10, 0),
        time(11, 0),
        time(12, 0),
        time(13, 0),
    ]
    start_times_afternoon = [time(17, 0), time(18, 0), time(19, 0)]

    today = date.today()
    days_offsets = list(range(-15, 15))

    for worker in workers:
        for offset in days_offsets:
            schedule_date = today + timedelta(days=offset)
            # Saltar fines de semana
            if schedule_date.weekday() >= 5:
                continue

            for start_time in start_times_morning + start_times_afternoon:
                end_time = (
                    datetime.combine(schedule_date, start_time) + timedelta(hours=1)
                ).time()
                Schedule.objects.create(
                    worker=worker,
                    date=schedule_date,
                    start_time=start_time,
                    end_time=end_time,
                    available=True,
                )
    print("Horarios creados con éxito")


def create_services():
    workers = list(Worker.objects.all())
    services = [
        {
            "name": "Rehabilitación de lesiones",
            "description": "Sesión de fisioterapia para rehabilitación y recuperación de lesiones.",
            "price": round(random.uniform(40.0, 80.0), 2),
            "image": "rehabilitacion.jpg",
        },
        {
            "name": "Evaluación inicial de fisioterapia",
            "description": "Evaluación inicial de fisioterapia para determinar el tratamiento adecuado.",
            "price": round(random.uniform(30.0, 60.0), 2),
            "image": "consulta_virtual.jpeg",
        },
        {
            "name": "Pilates terapéutico",
            "description": "Clase de pilates terapéutico para mejorar la postura y fortalecer el cuerpo.",
            "price": round(random.uniform(40.0, 90.0), 2),
            "image": "pilates.jpeg",
        },
    ]

    for service in services:
        with open(f"media/service_images/{service['image']}", "rb") as img_file:
            service_obj = Service.objects.create(
                name=service["name"],
                description=service["description"],
                price=service["price"],
                image=File(img_file, name=service["image"]),
            )
        num_workers = random.randint(1, 3)
        random_workers = random.sample(workers, num_workers)
        for worker in random_workers:
            service_obj.workers.add(worker)

    print("Servicios creados con éxito")


def create_offers():
    services = Service.objects.all()

    offers = [
        {
            "name": "Oferta",
            "description": f"Obtén un {random.randint(10, 30)}% de descuento en {service.name}.",
            "discount": round(random.uniform(10.0, 30.0), 2),
            "start_date": timezone.make_aware(
                fake.date_time_between(start_date="-30d", end_date="now")
            ),
            "end_date": timezone.make_aware(
                fake.date_time_between(start_date="now", end_date="+30d")
            ),
            "service": service,
        }
        for service in services
    ]

    for offer_data in offers:
        offer = Offer.objects.create(
            name=offer_data["name"],
            description=offer_data["description"],
            discount=offer_data["discount"],
            start_date=offer_data["start_date"],
            end_date=offer_data["end_date"],
        )
        offer.services.add(offer_data["service"])

    print("Ofertas creadas con éxito")


def find_eligible_worker(service_id):
    workers_offering_service = Service.objects.get(id=service_id).workers.filter(
        schedules__available=True
    )
    if workers_offering_service:
        return random.choice(workers_offering_service)
    return None


def create_appointments():
    clients = Client.objects.all()
    services = Service.objects.all()

    if not services:
        print("No hay servicios disponibles.")
        return

    today = date.today()
    days_offsets = list(range(-15, 15))  # 15 días en el pasado y 15 días en el futuro

    for i, client in enumerate(clients):
        chosen_service = random.choice(services)
        eligible_worker = find_eligible_worker(chosen_service.id)

        if not eligible_worker:
            print(
                f"No se encontró un trabajador elegible para el servicio {chosen_service.name}."
            )
            continue

        for offset in days_offsets:
            appointment_date = today + timedelta(days=offset)
            # Saltar fines de semana
            if appointment_date.weekday() >= 5:
                continue

            chosen_schedule = Schedule.objects.filter(
                worker=eligible_worker, available=True, date=appointment_date
            ).first()

            # Si no se encuentra un horario disponible en la fecha específica, no crear la cita
            if not chosen_schedule:
                print(
                    f"No se encontró un horario disponible para el trabajador {eligible_worker.user.first_name} el {appointment_date}."
                )
                continue

            # Determinar el estado de la cita
            if offset < 0:
                status = random.choice(["COMPLETED", "CANCELLED"])
            else:
                status = "CONFIRMED"

            appointment = Appointment.objects.create(
                client=client,
                worker=eligible_worker,
                service=chosen_service,
                schedule=chosen_schedule,
                description=fake.text(max_nb_chars=100),
                status=status,
                modality=random.choice(["VIRTUAL", "IN_PERSON"]),
            )
            chosen_schedule.available = False
            chosen_schedule.save()

            if status == "COMPLETED":
                # Crear informe y asignarlo a la cita
                inform = Inform.objects.create(
                    relevant_information=fake.text(max_nb_chars=100),
                    diagnostic=fake.text(max_nb_chars=100),
                    treatment=fake.text(max_nb_chars=100),
                )
                appointment.inform = inform
                appointment.save()

            # Crear factura y asignarla a la cita
            Invoice.objects.create(appointment=appointment)

            # Crear valoración solo para una fracción de las citas completadas
            if status == "COMPLETED" and random.random() < 0.3:  # 30% de probabilidad
                Rating.objects.create(
                    client=client,
                    appointment=appointment,
                    rate=random.randint(1, 5),
                    opinion=fake.text(max_nb_chars=100),
                )

            # Crear historial médico
            MedicalHistory.objects.create(
                client=client,
                title=f"Historial de {chosen_service.name}",
                description=f"Paciente con {fake.word()} tratado con {chosen_service.name}.",
            )

    print(
        "Citas, informes, facturas, valoraciones e historiales médicos creados con éxito."
    )


def create_resources():
    workers = Worker.objects.all()
    resource_images = ["lumbares.jpg", "hombro.jpg", "alimentacion.jpeg"]
    resources = [
        {
            "title": "Ejercicios para el dolor lumbar",
            "description": "Una guía completa de ejercicios para aliviar el dolor lumbar.",
            "resource_type": "FILE",
            "url": "https://www.comunidad.madrid/hospital/infantasofia/sites/infantasofia/files/inline-files/columna%20lumbar.pdf",
        },
        {
            "title": "Ejercicios terapéuticos para mejorar la movilidad del hombro",
            "description": "Una serie de ejercicios para mejorar la movilidad del hombro.",
            "resource_type": "URL",
            "url": "https://youtu.be/bFWrgXEJ3rQ?si=QBLacq87LjnDJjDK",
        },
        {
            "title": "Guía de alimentación saludable",
            "description": "Una guía de alimentación saludable para mejorar tu bienestar.",
            "resource_type": "FILE",
            "url": "https://www.euskadi.eus/contenidos/informacion/alim_sal_material/es_def/adjuntos/guia_alim_saldudable_castellano.pdf",
        },
    ]

    # Asegúrate de que hay suficientes imágenes para los recursos
    if len(resource_images) < len(resources):
        raise ValueError("No hay suficientes imágenes para los recursos.")

    for i, resource in enumerate(resources):
        resource_obj = Resource.objects.create(
            author=random.choice(workers).user,
            title=resource["title"],
            description=resource["description"],
            resource_type=resource["resource_type"],
            url=resource["url"],
        )
        resource_image_path = f"media/resources_images/{resource_images[i]}"
        with open(resource_image_path, "rb") as img_file:
            resource_obj.image_preview.save(
                os.path.basename(resource_image_path), File(img_file), save=True
            )

    print("Recursos creados con éxito")


def create_conversations_and_messages():
    users = list(CustomUser.objects.all())
    for _ in range(5):
        participants = random.sample(users, 2)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)

        for _ in range(3):
            sender = random.choice(participants)
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                content=fake.text(max_nb_chars=200),
                timestamp=fake.date_time_this_year(),
            )

    print("Conversaciones y mensajes creados con éxito")


def create_notifications():
    users = CustomUser.objects.exclude(owner__isnull=False)
    for user in users:
        Notification.objects.create(
            user=user,
            message=f"Tienes un recordatorio importante",
            type="REMINDER",
        )
    print("Notificaciones creadas con éxito")


def create_past_appointment_notifications():
    past_appointments = Appointment.objects.filter(
        schedule__date__lt=timezone.now().date(), status="COMPLETED"
    )

    for appointment in past_appointments:
        Notification.objects.create(
            user=appointment.client.user,
            message=f"Recordatorio de tu cita para {appointment.service} el {appointment.schedule.date} a las {appointment.schedule.start_time}",
            type=Notification.REMINDER,
        )

    print("Notificaciones de citas pasadas creadas con éxito")


if __name__ == "__main__":
    root_path = "apps"
    modules = ["authentication", "clients", "workers", "owner", "chat"]

    remove_pycache_and_clean_migrations(root_path, modules)
    clean_db()
    run_migrations()
    create_users()
    create_schedules()
    create_services()
    create_offers()
    create_appointments()
    create_resources()
    create_conversations_and_messages()
    create_notifications()
    create_past_appointment_notifications()
    print("Base de datos poblada con éxito.")
