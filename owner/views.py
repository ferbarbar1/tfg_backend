from twilio.rest import Client
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AppointmentSerializer


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
    def post(self, request, format=None):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()

            # Si la cita es virtual, crear una sala de Twilio y actualizar el enlace de la reunión
            if appointment.modality == "VIRTUAL":
                room_name = f"Appointment {appointment.schedule.id}"
                meeting_link = create_twilio_room(room_name)
                if meeting_link:
                    appointment.meeting_link = meeting_link
                    appointment.save()
                else:
                    print("Could not create Twilio room.")

            return Response(
                AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
