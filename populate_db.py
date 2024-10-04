import os
import shutil
import sqlite3
from datetime import time, date, datetime, timedelta
from django.core.files import File
import django
import random
from faker import Faker
from django.utils import timezone

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
    for i in range(5):
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
    past_days_offsets = [-60, -30, -2, -1]
    future_days_offsets = [0, 1, 2]

    for worker in workers:
        for offset in past_days_offsets + future_days_offsets:
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
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "price": round(random.uniform(50.0, 500.0), 2),
            "image": f"servicio{random.randint(1, 3)}.jpg",
        }
        for _ in range(4)
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
            "name": f"Oferta {i+1}",
            "description": fake.text(max_nb_chars=200),
            "discount": round(random.uniform(5.0, 50.0), 2),
            "start_date": timezone.make_aware(
                fake.date_time_between(start_date="-30d", end_date="now")
            ),
            "end_date": timezone.make_aware(
                fake.date_time_between(start_date="now", end_date="+30d")
            ),
        }
        for i in range(3)
    ]

    for offer_data in offers:
        offer = Offer.objects.create(**offer_data)
        num_services = random.randint(1, len(services))
        random_services = random.sample(list(services), num_services)
        offer.services.add(*random_services)

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
    days_offsets = [-60, -30, -2, -1, 0, 1, 2]  # Días pasados, hoy y días futuros

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
            if not chosen_schedule:
                print(
                    f"No se encontró un horario disponible para el trabajador {eligible_worker.user.first_name} el {appointment_date}."
                )
                continue

            appointment = Appointment.objects.create(
                client=client,
                worker=eligible_worker,
                service=chosen_service,
                schedule=chosen_schedule,
                description=fake.text(max_nb_chars=100),
                status=random.choice(["CONFIRMED", "COMPLETED"]),
                modality=random.choice(["VIRTUAL", "IN_PERSON"]),
            )
            chosen_schedule.available = False
            chosen_schedule.save()

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

            # Crear valoración
            Rating.objects.create(
                client=client,
                appointment=appointment,
                rate=random.randint(1, 5),
                opinion=fake.text(max_nb_chars=100),
            )

            # Crear historial médico
            MedicalHistory.objects.create(
                client=client,
                title=fake.word(),
                description=fake.text(max_nb_chars=200),
            )

    print(
        "Citas, informes, facturas, valoraciones e historiales médicos creados con éxito."
    )


def create_resources():
    authors = CustomUser.objects.all()
    for i in range(10):
        Resource.objects.create(
            author=random.choice(authors),
            title=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            resource_type=random.choice(["FILE", "URL"]),
            url=fake.url(),
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
    users = CustomUser.objects.all()
    for user in users:
        Notification.objects.create(
            user=user,
            message=f"Tienes un recordatorio importante",
            type="REMINDER",
        )
    print("Notificaciones creadas con éxito")


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
    print("Base de datos poblada con éxito.")
