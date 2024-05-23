from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stripe
from owner.models import Service
from owner.serializers import AppointmentSerializer
import requests


# Asegúrate de que la clave API de Stripe se establezca de manera segura
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_zoom_access_token(auth_code):
    token_url = "https://zoom.us/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": settings.ZOOM_REDIRECT_URI,
    }
    token_headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(settings.ZOOM_CLIENT_ID, settings.ZOOM_CLIENT_SECRET)}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post(token_url, data=token_data, headers=token_headers)
    return response.json()


def create_zoom_meeting(
    access_token, topic="Virtual Appointment", start_time=None, duration=30
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
        return Response(tokens)


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


# Copilot
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
            "status": "PENDING",
            "modality": metadata["modality"],
        }

        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save()

            if appointment.modality == "VIRTUAL":
                access_token = request.session.get("zoom_access_token")
                print("Zoom access token from session:", access_token)
                if access_token:
                    start_time_str = f"{appointment.schedule.date}T{appointment.schedule.start_time}Z"
                    zoom_response = create_zoom_meeting(
                        access_token,
                        f"Appointment {appointment.id}",
                        start_time=start_time_str,
                    )
                    print("Zoom API response:", zoom_response)
                    if "join_url" in zoom_response:
                        appointment.meeting_link = zoom_response["join_url"]
                        appointment.save()
                    else:
                        print("Error creating Zoom meeting:", zoom_response)
                else:
                    print("Zoom access token is missing.")

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


# chatgpt

"""
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
            "status": "PENDING",
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
                # Crear el InvoiceItem
                invoice_item = stripe.InvoiceItem.create(
                    customer=customer.id,
                    amount=session.get(
                        "amount_total"
                    ),  # Asegurarse de usar el valor correcto
                    currency=session.get("currency"),
                    description="Appointment booking",
                )
                # Crear la factura
                invoice = stripe.Invoice.create(
                    customer=customer.id,
                    auto_advance=False,  # No auto-finalizar la factura
                )

                # Finalizar la factura explícitamente
                finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)

                return Response(
                    {"success": "Appointment created and invoice issued successfully"},
                    status=status.HTTP_200_OK,
                )
            except stripe.error.StripeError as e:
                return Response(
                    {"error": "Stripe error: " + str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif event["type"] == "invoice.finalized":
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]

        try:
            # Enviar correo electrónico con el enlace de la factura
            email_message = f"Your appointment has been successfully booked. You can view and download your invoice here: {invoice['invoice_pdf']}"
            customer = stripe.Customer.retrieve(customer_id)
            send_mail(
                "Appointment Confirmation",
                email_message,
                settings.EMAIL_HOST_USER,
                [customer["email"]],
                fail_silently=False,
            )
        except stripe.error.StripeError as e:
            return Response(
                {"error": "Stripe error: " + str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"success": "Invoice finalized and email sent successfully"},
            status=status.HTTP_200_OK,
        )

    return Response(
        {"message": "Event type not handled"}, status=status.HTTP_202_ACCEPTED
    )
"""
