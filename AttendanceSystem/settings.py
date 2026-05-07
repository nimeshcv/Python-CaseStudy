from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured

# Try to import production helpers
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# Helper function for boolean env vars
def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.lower()
    return normalized in ("1", "true", "yes", "on")

ON_RENDER = "RENDER" in os.environ
DEBUG = env_bool("DEBUG", default=not ON_RENDER)

# --- SECURITY ---
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if not ON_RENDER:
        SECRET_KEY = "django-insecure-local-development-key"
    else:
        # This will cause a 500 if not set in Render Dashboard
        raise ImproperlyConfigured("Set the SECRET_KEY environment variable in Render.")

ALLOWED_HOSTS = ["*"]
render_external_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_external_hostname:
    ALLOWED_HOSTS.append(render_external_hostname)

if ON_RENDER:
    ALLOWED_HOSTS.append(".onrender.com")

if DEBUG or not ON_RENDER:
    ALLOWED_HOSTS.extend(["127.0.0.1", "localhost", "0.0.0.0"])

# CSRF Settings
CSRF_TRUSTED_ORIGINS = []
if render_external_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_external_hostname}")
if ON_RENDER:
    CSRF_TRUSTED_ORIGINS.append("https://*.onrender.com")

# --- APPS & MIDDLEWARE ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "students", # Your app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Moved up for reliability
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "AttendanceSystem.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "students.context_processors.user_role",
            ],
        },
    },
]

WSGI_APPLICATION = "AttendanceSystem.wsgi.application"

# --- DATABASE ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and dj_database_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- STATIC FILES ---
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")] # Ensure this folder exists or remove line

# WhiteNoise storage configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- PRODUCTION SECURITY ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- OTHER SETTINGS ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"