from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json
from clients.models import Client
from owner.models import Service
from workers.models import Worker, Schedule, Appointment

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        # Asumiendo que recibes estos IDs desde el frontend
        service_id = request.data.get("service_id")
        client_id = request.data.get("client_id")
        worker_id = request.data.get("worker_id")
        schedule_id = request.data.get("schedule_id")

        service = get_object_or_404(Service, id=service_id)

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {"name": service.name},
                            "unit_amount": int(float(service.price) * 100),
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=settings.SITE_URL
                + "/?success=true&session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.SITE_URL + "/?canceled=true",
                metadata={
                    "client_id": client_id,
                    "worker_id": worker_id,
                    "service_id": service_id,
                    "schedule_id": schedule_id,
                },
            )
            return Response(
                {"sessionId": checkout_session.id}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser


@api_view(["POST"])
def webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        session = event["data"]["object"]
    except ValueError:
        # Invalid payload
        return Response(
            {"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return Response(
            {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
        )
    metadata = session.get("metadata", {})
    print("Metadata:", metadata)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        # Verificar que la metadata necesaria existe
        metadata_required_keys = ["client_id", "worker_id", "service_id", "schedule_id"]
        if not all(
            key in session.get("metadata", {}) for key in metadata_required_keys
        ):
            return Response(
                {"error": "Missing required metadata"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extraer metadata
        metadata = session["metadata"]
        client_id = metadata["client_id"]
        worker_id = metadata["worker_id"]
        service_id = metadata["service_id"]
        schedule_id = metadata["schedule_id"]

        # Obtener las instancias de los modelos usando los IDs
        client = get_object_or_404(Client, id=client_id)
        worker = get_object_or_404(Worker, id=worker_id)
        service = get_object_or_404(Service, id=service_id)
        schedule = get_object_or_404(Schedule, id=schedule_id)

        # Crear o actualizar el Appointment aquí
        appointment = Appointment.objects.create(
            client=client,
            worker=worker,
            service=service,
            schedule=schedule,
            status="PENDING",  # o cualquier lógica para establecer el estado
            modality="IN_PERSON",  # o basado en alguna lógica o metadata
            # meeting_link se puede generar aquí si es necesario
        )

        return Response(
            {"success": "Appointment created successfully"}, status=status.HTTP_200_OK
        )

    # Responder al webhook con éxito incluso si el evento no se maneja
    return Response({"message": "Event type not handled"}, status=status.HTTP_200_OK)
