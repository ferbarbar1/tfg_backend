from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stripe
from owner.models import Service
from owner.serializers import AppointmentSerializer
import logging

logger = logging.getLogger(__name__)


# Asegúrate de que la clave API de Stripe se establezca de manera segura
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        # Validación de los IDs recibidos en la petición
        service_id = request.data.get("service_id")
        client_id = request.data.get("client_id")
        schedule_id = request.data.get("schedule_id")
        description = request.data.get("description", "")  # Valor por defecto
        modality = request.data.get("modality")

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
                    "service_id": service_id,
                    "schedule_id": schedule_id,
                    "description": description,
                    "modality": modality,
                },
            )
            return Response(
                {"sessionId": checkout_session.id}, status=status.HTTP_200_OK
            )
        except stripe.error.StripeError as e:
            # Manejo específico de errores de Stripe
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Manejo de excepciones generales
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["POST"])
def webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Carga útil inválida
        return Response(
            {"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.SignatureVerificationError:
        # Firma inválida
        return Response(
            {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Procesamiento del evento
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        metadata_required_keys = [
            "client_id",
            "service_id",
            "schedule_id",
            "description",
            "modality",
        ]
        if not all(key in metadata for key in metadata_required_keys):
            return Response(
                {"error": "Missing required metadata"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment_data = {
            "client_id": metadata["client_id"],
            "service_id": metadata["service_id"],
            "schedule_id": metadata["schedule_id"],
            "description": metadata["description"],
            "status": "PENDING",
            "modality": metadata["modality"],
        }

        logger.debug(f"Metadata received: {metadata}")
        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            serializer.save()
            logger.debug("Appointment created successfully")
            return Response(
                {"success": "Appointment created successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Manejo de eventos no procesados
    return Response(
        {"message": "Event type not handled"}, status=status.HTTP_202_ACCEPTED
    )
