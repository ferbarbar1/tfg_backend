from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Appointment
from chat.models import Notification


@shared_task
def send_appointment_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        schedule__date=tomorrow, status="CONFIRMED"
    )

    for appointment in appointments:
        send_mail(
            "Recordatorio de Cita",
            f"Hola {appointment.client.user.first_name},\n\nEste es un recordatorio de tu cita {appointment.modality} para {appointment.service} con {appointment.worker.user.first_name} {appointment.worker.user.last_name} mañana a las {appointment.schedule.start_time}.\n\n¡Te esperamos!",
            "fisioterappia.clinic@gmail.com",
            [appointment.client.user.email],
            fail_silently=False,
        )

        Notification.objects.create(
            user=appointment.client.user,
            message=f"Recordatorio de cita para {appointment.service} mañana a las {appointment.schedule.start_time}",
            type=Notification.REMINDER,
        )
