from django.shortcuts import render, get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
import stripe
from owner.models import Service

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        service_id = request.data.get("service_id")
        service = get_object_or_404(Service, id=service_id)

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": service.name,
                            },
                            "unit_amount": int(float(service.price) * 100),
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=settings.SITE_URL
                + "/?success=true&session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.SITE_URL + "/?canceled=true",
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
