import os
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "core.settings"
)  # Reemplaza 'myproject.settings' con la ruta a tu archivo settings


def test_twilio_connection():
    url = "https://api.twilio.com/2010-04-01/Accounts.json"
    auth = HTTPBasicAuth(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        print("Conexión exitosa a la API de Twilio.")
    else:
        print(f"Error al conectar a la API de Twilio: {response.status_code}")


if __name__ == "__main__":
    test_twilio_connection()
