"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from corsheaders.defaults import default_headers
import os
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", default="your secret key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = "RAILWAY" not in os.environ

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "tfgbackend-production.up.railway.app",
]

RAILWAY_EXTERNAL_HOSTNAME = os.environ.get("RAILWAY_EXTERNAL_HOSTNAME")

if RAILWAY_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RAILWAY_EXTERNAL_HOSTNAME)

# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "coreapi",
    "authentication",
    "owner",
    "workers",
    "clients",
    "chat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://tfgfrontend-production.up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://tfgfrontend-production.up.railway.app",
]

CORS_ALLOW_HEADERS = default_headers

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# This setting informs Django of the URI path from which your static files will be served to users
# Here, they well be accessible at your-domain.onrender.com/static/... or yourcustomdomain.com/static/...
STATIC_URL = "/static/"

# This production code might break development mode, so we check whether we're in DEBUG mode
if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Specify the custom user model
AUTH_USER_MODEL = "authentication.CustomUser"


# Needed to authenticate users and document the API
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

STRIPE_PUBLIC_KEY = "pk_test_51PFdYTGzZooPGUyPyarTnl6RMGFS0Zkll6iKQcpYRK0sICx2lokA4BEXIoxm1j4n1OmvkOP48mYaTaGBpsPfzs5Y0012QYjWvu"
STRIPE_SECRET_KEY = "sk_test_51PFdYTGzZooPGUyPHktEqWtQFsTCuA7E2jEczM1tGd5A2YThlAc506gxr0bEdlFjjd33M4gjSdlwrkRUCMzKaTJo00K22vfhDk"
STRIPE_WEBHOOK_SECRET = (
    "whsec_d06fb4ec31116b0dca70cd584f1a552e90dfe85d205cc44aea9b45ed006b86a4"
)

# Configuración de correo electrónico
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Por ejemplo, 'smtp.gmail.com' para Gmail
EMAIL_PORT = 587  # Puerto típico para correo seguro
EMAIL_USE_TLS = True  # Usar TLS
EMAIL_HOST_USER = "fisioterappia.clinic@gmail.com"
EMAIL_HOST_PASSWORD = "ynbq fzoz vxpw aqlz"

SITE_URL = "http://localhost:5173"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Necesario para Django Channels
ASGI_APPLICATION = "core.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        # Para producción, usa Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    },
}

# Configuración de Celery (para crear horarios automaticamente)
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

from celery.schedules import schedule, crontab

CELERY_BEAT_SCHEDULE = {
    "create-schedules-every-two-weeks": {
        "task": "workers.tasks.create_schedules_for_all_workers",
        "schedule": schedule(run_every=14 * 24 * 60 * 60),  # Cada 14 días
    },
    "send-appointment-reminders-every-day": {
        "task": "clients.tasks.send_appointment_reminders",
        "schedule": crontab(hour=7, minute=30),  # A las 7:30 AM
    },
}
