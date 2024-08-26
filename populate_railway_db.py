import os
from datetime import time, date, datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.core.management import call_command
from django.apps import apps
from authentication.models import CustomUser, Owner, Client, Worker
from workers.models import Schedule
from workers.models import Appointment
from owner.models import Service
from clients.models import Rating
import random


def delete_all_data():
    for model in apps.get_models():
        model.objects.all().delete()
    print("Todos los datos han sido eliminados")


def run_migrations():
    # Ejecuta 'makemigrations' para todas las aplicaciones
    call_command("makemigrations")

    # Ejecuta 'migrate' para aplicar las migraciones
    call_command("migrate")


def create_users():
    # Crear propietario
    if not CustomUser.objects.filter(email="owner@example.com").exists():
        owner_user = CustomUser.objects.create_user(
            "owner",
            "owner@example.com",
            "ownerpassword",
            first_name="Owner",
            last_name="User",
        )
        Owner.objects.create(user=owner_user)

    # Crear superusuario
    if not CustomUser.objects.filter(email="superuser@example.com").exists():
        super_user = CustomUser.objects.create_superuser(
            "superuser",
            "superuser@example.com",
            "superuser",
            first_name="Super",
            last_name="User",
        )

    # Crear varios trabajadores y clientes
    for i in range(5):
        if not CustomUser.objects.filter(email=f"worker{i}@example.com").exists():
            worker_user = CustomUser.objects.create_user(
                f"worker{i}",
                f"worker{i}@example.com",
                "workerpassword",
                first_name=f"Worker{i}",
                last_name="User",
            )
            Worker.objects.create(
                user=worker_user,
                specialty="Especialidad",
            )
        if not CustomUser.objects.filter(email=f"client{i}@example.com").exists():
            client_user = CustomUser.objects.create_user(
                f"client{i}",
                f"client{i}@example.com",
                "clientpassword",
                first_name=f"Client{i}",
                last_name="User",
            )
            Client.objects.create(
                user=client_user,
            )

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

    # Fecha de inicio para los horarios
    start_date = date.today()

    for worker in workers:
        for day in range(5):  # 0 = Lunes, 1 = Martes, ..., 4 = Viernes
            # Calcula la fecha del horario
            schedule_date = start_date + timedelta(days=day)
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


def create_appointments():
    clients = Client.objects.all()
    schedules = Schedule.objects.filter(available=True)

    for client in clients:
        if schedules:
            chosen_schedule = schedules.first()
            Appointment.objects.create(
                client=client,
                worker=chosen_schedule.worker,
                schedule=chosen_schedule,
                description="Cita de ejemplo",
            )
            chosen_schedule.available = False
            chosen_schedule.save()

    print("Citas creadas con éxito")


def create_services():
    workers = list(Worker.objects.all())
    service = Service.objects.create(
        name="Servicio de ejemplo",
        description="Descripción de ejemplo",
        price=100.00,
    )
    num_workers = random.randint(1, 2)  # Número aleatorio de trabajadores: 1 o 2
    random_workers = random.sample(
        workers, num_workers
    )  # Selecciona especialistas aleatorios
    for worker in random_workers:
        service.workers.add(worker)
    print("Servicios creados con éxito")


def create_ratings():
    # Obtén los primeros dos trabajadores
    workers = Worker.objects.all()[:2]

    # Obtén los primeros dos clientes
    clients = Client.objects.all()[:2]

    # Obtén el primer servicio
    service = Service.objects.first()

    # Crea dos calificaciones
    for i in range(2):
        Rating.objects.create(
            worker=workers[i],
            client=clients[i],
            service=service,
            rate=i + 3,  # Puntuaciones de 3 y 4
            opinion=f"Opinión {i+1}",
            date=datetime.now(),  # Añade la fecha y hora actual
        )

    print("Calificaciones creadas con éxito")


def populate_db():
    print("Eliminando todos los datos existentes... Por favor espera")
    delete_all_data()
    print("Ejecutando migraciones... Por favor espera")
    run_migrations()
    print("Poblando la base de datos... Por favor espera")
    create_users()
    create_schedules()
    create_appointments()
    create_services()
    create_ratings()
    print("Población completada con éxito")


if __name__ == "__main__":
    populate_db()
