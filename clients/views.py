from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from xhtml2pdf import pisa
from io import BytesIO
from owner.models import Service, Invoice
from .serializers import AppointmentSerializer
from django.template.loader import render_to_string
from .models import Appointment
from chat.models import Notification
from datetime import datetime
from workers.models import Schedule

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
        schedule = get_object_or_404(Schedule, id=schedule_id)

        # Validar que la fecha del appointment no sea pasada
        if schedule.date < datetime.now().date():
            return Response(
                {"error": "The appointment date must be in the future."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

            # Crear la cita y almacenar el ID de la sesión de Stripe
            appointment_data = {
                "client_id": client_id,
                "service_id": service_id,
                "schedule_id": schedule_id,
                "description": description,
                "status": "CONFIRMED",
                "modality": modality,
                "stripe_session_id": checkout_session.id,
            }
            serializer = AppointmentSerializer(data=appointment_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)

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


class CreateAppointmentByOwnerView(APIView):
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
            "status": "CONFIRMED",
            "modality": modality,
        }

        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save()
            return Response(
                {"success": "Appointment created successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            "stripe_session_id": session.id,
        }

        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save()

            # Crear la factura asociada a la cita
            invoice = Invoice.objects.create(appointment=appointment)

            logo_url = request.build_absolute_uri(settings.MEDIA_URL + "logo/logo.png")

            # Generar el contenido HTML para la factura
            html_string = render_to_string(
                "invoice_email.html",
                {
                    "appointment": appointment,
                    "invoice": invoice,
                    "logo_url": logo_url,
                },
            )

            # Convertir HTML a PDF usando xhtml2pdf
            pdf_file = BytesIO()
            pisa_status = pisa.CreatePDF(
                BytesIO(html_string.encode("utf-8")), dest=pdf_file
            )

            if pisa_status.err:
                return Response(
                    {"error": "Error generating PDF"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Preparar el correo electrónico con la factura adjunta en PDF
            subject = "Confirmación de Cita"
            body = (
                f"Su cita para el servicio '{appointment.service.name}' "
                f"el {appointment.schedule.date}, {appointment.schedule.start_time} ha sido confirmada. "
                "Encontrará adjunta la factura."
                "\n\n¡Gracias por elegirnos! "
                "\nFisioterAppIA Clinic"
            )
            email = EmailMessage(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [session.get("customer_details").get("email")],
            )
            email.attach(
                f"invoice_{invoice.id}.pdf", pdf_file.getvalue(), "application/pdf"
            )

            email.send()

            return Response(
                {"success": "Appointment and invoice created successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"message": "Event type not handled"}, status=status.HTTP_202_ACCEPTED
    )


class CancelAppointmentView(APIView):
    def post(self, request, *args, **kwargs):
        appointment_id = request.data.get("appointment_id")
        user = request.user

        # Obtener la cita
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Procesar la devolución de dinero utilizando la API de Stripe
        try:
            # Obtener el ID de la sesión de pago de Stripe desde la metadata de la cita
            stripe_session_id = appointment.stripe_session_id
            if not stripe_session_id:
                return Response(
                    {
                        "error": "No se encontró el ID de la sesión de Stripe para esta cita"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Obtener la sesión de pago de Stripe
            session = stripe.checkout.Session.retrieve(stripe_session_id)

            # Crear la devolución de dinero
            refund = stripe.Refund.create(payment_intent=session.payment_intent)

            # Actualizar el estado de la cita a "CANCELLED"
            appointment.status = "CANCELLED"
            appointment.save()

            worker = appointment.worker.user
            Notification.objects.create(
                user=worker,
                message=f"La cita del cliente {appointment.client.user.username} para el servicio '{appointment.service.name}' "
                f"con fecha {appointment.schedule.date}, {appointment.schedule.start_time} ha sido cancelada.",
            )

            # Enviar una notificación por correo electrónico al usuario
            subject = "Cancelación de Cita"
            body = (
                f"Su cita para el servicio '{appointment.service.name}' "
                f"el {appointment.schedule.date}, {appointment.schedule.start_time} ha sido cancelada. "
                "El reembolso ha sido procesado exitosamente."
                "\n¡Gracias por elegirnos!"
                "\n"
                "\nFisioterAppIA Clinic"
            )
            email = EmailMessage(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [appointment.client.user.email],
            )
            email.send()

            return Response(
                {"success": "Cita cancelada y reembolso procesado exitosamente"},
                status=status.HTTP_200_OK,
            )
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Ocurrió un error inesperado"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
