import os
import shutil
import sqlite3
from datetime import time, date, datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.core.management import call_command
from authentication.models import CustomUser, Owner, Client, Worker
from workers.models import Schedule
from workers.models import Appointment
from owner.models import Service
from clients.models import Rating
import random


def remove_pycache_and_clean_migrations(root_path, modules):
    for module in modules:
        # Ruta del módulo
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

        # Reiniciar los IDs de las tablas a 1
        cur.execute("DELETE FROM sqlite_sequence")
        conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def run_migrations():
    # Ejecuta 'makemigrations' para todas las aplicaciones
    call_command("makemigrations")

    # Ejecuta 'migrate' para aplicar las migraciones
    call_command("migrate")


def create_users():
    # Crear propietario
    owner_user = CustomUser.objects.create_user(
        "owner", "owner@example.com", "ownerpassword"
    )
    Owner.objects.create(user=owner_user)

    # Crear superusuario
    super_user = CustomUser.objects.create_superuser(
        "superuser", "superuser@example.com", "superuser"
    )

    # Crear varios trabajadores y clientes
    for i in range(5):
        worker_user = CustomUser.objects.create_user(
            f"worker{i}",
            f"worker{i}@example.com",
            "workerpassword",
        )
        Worker.objects.create(
            user=worker_user,
            salary=5000.00,
            specialty="Especialidad",
        )
        client_user = CustomUser.objects.create_user(
            f"client{i}",
            f"client{i}@example.com",
            "clientpassword",
        )
        Client.objects.create(
            user=client_user,
            subscription_plan="FREE",
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
        )

    print("Calificaciones creadas con éxito")


def populate_db():
    print("Limpiando archivos de migraciones y __pycache__... Por favor espera")
    # Ruta de la carpeta actual donde se encuentra el script
    root_path = "."
    # Lista de módulos a limpiar
    modules = ["authentication", "clients", "owner", "workers"]
    remove_pycache_and_clean_migrations(root_path, modules)
    print("Limpiando la base de datos... Por favor espera")
    clean_db()
    print("Ejecutando migraciones... Por favor espera")
    run_migrations()
    print("Poblando la base de datos... Por favor espera")
    create_users()
    create_schedules()
    create_appointments()
    create_services()
    create_ratings()
    print("Población completa!")


if __name__ == "__main__":
    populate_db()
