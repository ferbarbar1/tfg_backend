from twilio.rest import Client
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from workers.models import Appointment, Schedule
from .serializers import AppointmentSerializer
from django.db.models import Sum, F, ExpressionWrapper, fields
from datetime import timedelta
from .permissions import IsOwner


def create_twilio_room(room_name):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    try:
        room = client.video.rooms.create(unique_name=room_name)
        meeting_link = f"https://video.twilio.com/{room.sid}"
        print(f"Twilio room created: {meeting_link}")
        return meeting_link
    except Exception as e:
        print(f"Error creating Twilio room: {e}")
        return None


class CreateAppointmentView(APIView):
    permission_classes = [IsOwner]

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
        meeting_link = None
        if serializer.validated_data["modality"] == "VIRTUAL":
            room_name = "Appointment {}".format(
                schedule.id
            )  # Genera un nombre único para la sala
            meeting_link = create_twilio_room(room_name)
            if meeting_link is None:
                print("Could not create Twilio room.")

        appointment = Appointment(
            schedule=schedule, meeting_link=meeting_link, **serializer.validated_data
        )
        appointment.save()
        schedule.available = False
        schedule.save()
        return Response(
            AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED
        )

    def error_response(self, message):
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
