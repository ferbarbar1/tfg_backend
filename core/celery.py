# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración predeterminado de Django para el programa 'celery'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# Usar una cadena aquí significa que el worker no tiene que serializar
# el objeto de configuración para los hijos.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Cargar tareas de todos los módulos de aplicaciones registradas en Django.
app.autodiscover_tasks()
