from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from workers.models import Appointment, Schedule
from .serializers import AppointmentSerializer
from django.db.models import Sum, F, ExpressionWrapper, fields
from datetime import timedelta

"""
class CreateAppointmentView(APIView):
    def post(self, request, format=None):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            # Obtén el horario y el trabajador desde los datos de la cita
            schedule_id = serializer.validated_data.pop("schedule").id
            worker_id = serializer.validated_data["worker"].id

            # Busca el horario seleccionado
            schedule = Schedule.objects.filter(id=schedule_id, available=True).first()

            if schedule is not None:
                # Verifica que el trabajador asociado al horario es el mismo que el trabajador de la cita
                if schedule.worker.id != worker_id:
                    return Response(
                        {
                            "error": "El trabajador de la cita y el trabajador del horario no coinciden."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Comprueba que el trabajador no tenga más de 8 horarios asignados en un día
                appointments_same_day = Appointment.objects.filter(
                    worker__id=worker_id, schedule__date=schedule.date
                ).count()
                if appointments_same_day >= 8:
                    return Response(
                        {
                            "error": "El trabajador ya tiene 8 horarios asignados para este día."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Comprueba que la suma de todos los horarios asignados al trabajador no sume más de 40 horas semanales
                week_start = schedule.date - timedelta(days=schedule.date.weekday())
                week_end = week_start + timedelta(days=6)
                appointments_same_week = Appointment.objects.filter(
                    worker__id=worker_id, schedule__date__range=[week_start, week_end]
                )
                total_hours = appointments_same_week.aggregate(
                    total_hours=ExpressionWrapper(
                        Sum(F("schedule__end_time") - F("schedule__start_time")),
                        output_field=fields.DurationField(),
                    )
                )["total_hours"]
                if total_hours is not None and total_hours.total_seconds() / 3600 > 40:
                    return Response(
                        {
                            "error": "El trabajador ya tiene asignadas 40 horas para esta semana."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Si se encontró un horario disponible y se pasaron todas las comprobaciones, crea la cita y marca el horario como no disponible
                appointment = Appointment(
                    schedule=schedule, **serializer.validated_data
                )
                appointment.save()
                schedule.available = False
                schedule.save()

                return Response(
                    AppointmentSerializer(appointment).data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                # Si no se encontró un horario disponible, devuelve un error
                return Response(
                    {
                        "error": "No hay horarios disponibles para la especialidad requerida en el horario seleccionado."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""


class CreateAppointmentView(APIView):
    def post(self, request, format=None):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            schedule_id = serializer.validated_data.pop("schedule").id
            worker_id = serializer.validated_data["worker"].id

            schedule = self.get_schedule(schedule_id)

            if schedule is not None:
                if not self.is_worker_match(schedule, worker_id):
                    return self.error_response(
                        "Appointment worker and schedule worker do not match."
                    )

                if not self.is_daily_limit_reached(worker_id, schedule.date):
                    return self.error_response(
                        "The worker already has 8 schedules assigned for this day."
                    )

                if not self.is_weekly_limit_reached(worker_id, schedule.date):
                    return self.error_response(
                        "The worker already has 40 hours assigned for this week."
                    )

                return self.create_appointment_and_update_schedule(serializer, schedule)

            else:
                return self.error_response(
                    "No schedules available for the required specialty at the selected time."
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_schedule(self, schedule_id):
        return Schedule.objects.filter(id=schedule_id, available=True).first()

    def is_worker_match(self, schedule, worker_id):
        return schedule.worker.id == worker_id

    def is_daily_limit_reached(self, worker_id, date):
        appointments_same_day = Appointment.objects.filter(
            worker__id=worker_id, schedule__date=date
        ).count()
        return appointments_same_day < 8

    def is_weekly_limit_reached(self, worker_id, date):
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        appointments_same_week = Appointment.objects.filter(
            worker__id=worker_id, schedule__date__range=[week_start, week_end]
        )
        total_hours = appointments_same_week.aggregate(
            total_hours=ExpressionWrapper(
                Sum(F("schedule__end_time") - F("schedule__start_time")),
                output_field=fields.DurationField(),
            )
        )["total_hours"]
        return total_hours is None or total_hours.total_seconds() / 3600 <= 40

    def create_appointment_and_update_schedule(self, serializer, schedule):
        appointment = Appointment(schedule=schedule, **serializer.validated_data)
        appointment.save()
        schedule.available = False
        schedule.save()
        return Response(
            AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED
        )

    def error_response(self, message):
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
