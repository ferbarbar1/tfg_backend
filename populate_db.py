import os
import shutil
import sqlite3
from datetime import time, date, datetime, timedelta
from django.core.files import File
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.management import call_command
from authentication.models import CustomUser, Owner, Client, Worker
from workers.models import Schedule
from clients.models import Appointment
from owner.models import Service
from clients.models import Rating

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
                    f"No hay horarios disponibles para el trabajador {eligible_worker.user.username} en la fecha {appointment_date}."
                )
                continue

            status = "COMPLETED" if offset < 0 else "CONFIRMED"

            appointment = Appointment(
                client=client,
                worker=eligible_worker,
                schedule=chosen_schedule,
                service=chosen_service,
                description=fake.text(max_nb_chars=200),
                modality="VIRTUAL" if i % 2 == 0 else "IN_PERSON",
                status=status,
            )
            appointment.save()
            chosen_schedule.available = False
            chosen_schedule.save()

    print("Citas creadas con éxito.")


def create_ratings():
    completed_appointments = Appointment.objects.filter(status="COMPLETED")
    num_appointments = len(completed_appointments)

    for i in range(num_appointments):
        Rating.objects.create(
            appointment=completed_appointments[i],
            client=completed_appointments[i].client,
            rate=random.randint(1, 5),
            opinion=fake.text(max_nb_chars=200),
            date=datetime.now(),
        )

    print("Calificaciones creadas con éxito")


def populate_db():
    print("Limpiando archivos de migraciones y __pycache__... Por favor espera")
    root_path = "."
    modules = ["authentication", "clients", "owner", "workers", "chat"]
    remove_pycache_and_clean_migrations(root_path, modules)
    print("Limpiando la base de datos... Por favor espera")
    clean_db()
    print("Ejecutando migraciones... Por favor espera")
    run_migrations()
    print("Poblando la base de datos... Por favor espera")
    create_users()
    create_schedules()
    create_services()
    create_appointments()
    create_ratings()
    print("Población completa!")


if __name__ == "__main__":
    populate_db()
