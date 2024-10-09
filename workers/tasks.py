# tasks.py
from celery import shared_task
from datetime import datetime, timedelta, time
from .models import Schedule
from authentication.models import Worker

# Lista de días festivos
HOLIDAYS = [
    datetime(2024, 12, 25).date(),
    datetime(2025, 1, 1).date(),
]


@shared_task
def create_schedules_for_all_workers():
    workers = Worker.objects.all()
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30)  # Crear horarios para el próximo mes

    for worker in workers:
        current_date = start_date
        while current_date <= end_date:
            # Evitar fines de semana y días festivos
            if current_date.weekday() >= 5 or current_date in HOLIDAYS:
                current_date += timedelta(days=1)
                continue

            # Crear horarios de 9:00 a 14:00
            create_schedules_for_interval(worker, current_date, time(9, 0), time(14, 0))

            # Crear horarios de 17:00 a 19:00
            create_schedules_for_interval(
                worker, current_date, time(17, 0), time(19, 0)
            )

            current_date += timedelta(days=1)


def create_schedules_for_interval(
    worker, current_date, start_time, end_time, interval_minutes=60
):
    current_time = start_time
    while current_time < end_time:
        schedule_end_time = (
            datetime.combine(datetime.today(), current_time)
            + timedelta(minutes=interval_minutes)
        ).time()
        if schedule_end_time > end_time:
            break

        # Verificar si ya existe un horario para este trabajador en esta fecha y hora
        if not Schedule.objects.filter(
            worker=worker,
            date=current_date,
            start_time=current_time,
            end_time=schedule_end_time,
        ).exists():
            Schedule.objects.create(
                worker=worker,
                date=current_date,
                start_time=current_time,
                end_time=schedule_end_time,
                available=True,
            )

        current_time = schedule_end_time
