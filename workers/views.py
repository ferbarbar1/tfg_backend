from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Appointment, Schedule
from owner.serializers import AppointmentSerializer
from django.db.models import Sum, F, ExpressionWrapper, fields
from datetime import timedelta

"""
class CreateAppointmentView(APIView):
    def post(self, request, format=None):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            # Obtén el horario y la especialidad desde los datos de la cita
            schedule_id = serializer.validated_data.pop("schedule").id
            specialty = serializer.validated_data["worker"].specialty

            # Busca el horario seleccionado y verifica si hay un trabajador con la especialidad requerida disponible para ese horario
            schedule = Schedule.objects.filter(
                id=schedule_id, worker__specialty=specialty, available=True
            ).first()

            if schedule is not None:
                # Si se encontró un horario disponible, crea la cita y marca el horario como no disponible
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
            # Obtén el horario y la especialidad desde los datos de la cita
            schedule_id = serializer.validated_data.pop("schedule").id
            worker_id = serializer.validated_data["worker"].id

            # Busca el horario seleccionado y verifica si hay un trabajador con la especialidad requerida disponible para ese horario
            schedule = Schedule.objects.filter(
                id=schedule_id, worker__id=worker_id, available=True
            ).first()

            if schedule is not None:
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
