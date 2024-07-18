from django.shortcuts import redirect, get_object_or_404
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from clients.models import Appointment
import base64


def get_zoom_authorization_url():
    base_url = "https://zoom.us/oauth/authorize"
    client_id = settings.ZOOM_CLIENT_ID
    redirect_uri = settings.ZOOM_REDIRECT_URI
    scopes = "meeting:read:meeting meeting:write:meeting meeting:write:invite_links"
    return f"{base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}"


def get_zoom_access_token(auth_code):
    token_url = "https://zoom.us/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": settings.ZOOM_REDIRECT_URI,
    }

    client_creds = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    encoded_creds = base64.b64encode(client_creds.encode()).decode()

    token_headers = {
        "Authorization": f"Basic {encoded_creds}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(token_url, data=token_data, headers=token_headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        response.raise_for_status()


def create_zoom_meeting(
    access_token, topic="Virtual Appointment", start_time=None, duration=60
):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    meeting_details = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,
        "duration": duration,  # Duration in minutes
        "timezone": "UTC",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": True,
        },
    }

    response = requests.post(
        "https://api.zoom.us/v2/users/me/meetings",
        headers=headers,
        json=meeting_details,
    )

    return response.json()


class ZoomAuthView(APIView):
    def get(self, request, *args, **kwargs):
        auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={settings.ZOOM_CLIENT_ID}&redirect_uri={settings.ZOOM_REDIRECT_URI}"
        return redirect(auth_url)


class ZoomCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        auth_code = request.GET.get("code")
        tokens = get_zoom_access_token(auth_code)
        request.session["zoom_access_token"] = tokens["access_token"]

        # Redirigir a la vista de detalles del appointment
        appointment_id = request.session.get("appointment_id")
        if appointment_id:
            return redirect(f"/api/appointments/{appointment_id}/create_zoom_meeting/")
        return Response(
            {"error": "Appointment ID missing"}, status=status.HTTP_400_BAD_REQUEST
        )


class CreateZoomMeetingView(APIView):
    def post(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.modality != "VIRTUAL":
            return Response(
                {"error": "Appointment is not virtual"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = request.session.get("zoom_access_token")
        if not access_token:
            # Guardar el appointment_id en la sesión para usarlo después del callback de OAuth
            request.session["appointment_id"] = appointment_id
            return redirect(get_zoom_authorization_url())

        start_time_str = (
            f"{appointment.schedule.date}T{appointment.schedule.start_time}Z"
        )
        zoom_response = create_zoom_meeting(
            access_token, f"Appointment {appointment.id}", start_time=start_time_str
        )

        if "join_url" in zoom_response:
            appointment.meeting_link = zoom_response["join_url"]
            appointment.save()
            return redirect(
                f"/path/to/appointment/details/{appointment.id}/"
            )  # Redirigir a la vista de detalles del appointment
        else:
            return Response(
                {"error": "Error creating Zoom meeting", "details": zoom_response},
                status=status.HTTP_400_BAD_REQUEST,
            )
