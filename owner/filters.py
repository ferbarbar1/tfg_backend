from django_filters import rest_framework as filters
from .models import Invoice


class InvoiceFilter(filters.FilterSet):
    class Meta:
        model = Invoice
        fields = ["appointment"]
