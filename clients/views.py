from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from owner.models import Service
from .serializers import AppointmentSerializer

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

        # Ver si hay una oferta activa para el servicio
        discounted_price = service.get_discounted_price()

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {"name": service.name},
                            "unit_amount": int(float(discounted_price) * 100),
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


class CreateAppointmentView(APIView):
    def post(self, request, *args, **kwargs):
        service_id = request.data.get("service_id")
        client_id = request.data.get("client_id")
        schedule_id = request.data.get("schedule_id")
        description = request.data.get("description", "")
        modality = request.data.get("modality")

        appointment_data = {
            "client_id": client_id,
            "service_id": service_id,
            "schedule_id": schedule_id,
            "description": description,
            "status": "PENDING",
            "modality": modality,
        }

        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save()
            return Response(
                {"success": "Appointment created successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return Response(
            {"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.SignatureVerificationError:
        return Response(
            {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
        )

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
            "status": "CONFIRMED",
            "modality": metadata["modality"],
        }

        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save()

            customer_email = session.get("customer_details").get("email")
            existing_customers = stripe.Customer.list(email=customer_email).data
            if existing_customers:
                customer = existing_customers[0]
            else:
                customer = stripe.Customer.create(email=customer_email)

            try:
                invoice_item = stripe.InvoiceItem.create(
                    customer=customer.id,
                    amount=int(float(session.get("amount_total"))),
                    currency=session.get("currency"),
                    description="Appointment booking",
                )
                invoice = stripe.Invoice.create(
                    customer=customer.id,
                    auto_advance=False,  # No Auto-finalizar la factura
                )

                finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)
                email_message = f"Your appointment has been successfully booked. You can view and download your invoice here: {finalized_invoice.invoice_pdf}"
                send_mail(
                    "Appointment Confirmation",
                    email_message,
                    settings.EMAIL_HOST_USER,
                    [customer_email],
                    fail_silently=False,
                )
            except stripe.error.StripeError as e:
                return Response(
                    {"error": "Stripe error: " + str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"success": "Appointment created successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"message": "Event type not handled"}, status=status.HTTP_202_ACCEPTED
    )
