# ruff: noqa: ERA001, E501
"""
Production-ready Django settings file.
For local development, use .default file to override necessary settings.
"""

import os
from pathlib import Path

import dj_database_url
from uncouple import Config, StringList

#############################
# Directories
#############################
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
APPS_DIR = BASE_DIR / "apps"

# Load .env file manually to ensure decouple can find the variables
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")  # Remove quotes if present
                # Only set if not already in environment (env vars take precedence)
                if key not in os.environ:
                    os.environ[key] = value


#############################
# Configuration Classes
#############################
class DjangoConfig(Config):
    """Django general configuration"""

    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: StringList = ["*"]
    ADMIN_PATH: str = "admin/"
    ADMINS: str = ""
    MEDIA_URL: str = "/media/"
    TIME_ZONE: str = "UTC"
    FRONTEND_URL: str = "http://localhost:3000"
    AUTH_USER_MODEL: str = "users.User"
    LOGIN_REDIRECT_URL: str = "/"
    LOGIN_URL: str = "/admin/login/"
    DATABASE_URL: str = "sqlite:///db.sqlite3"
    LOG_LEVEL: str = "INFO"
    SECURE_SSL_REDIRECT: bool = False


class CeleryConfig(Config):
    """Celery configuration"""

    BROKER_URL: str = ""
    RESULT_BACKEND: str = "django-db"
    TASK_TIME_LIMIT: int = 600
    TASK_SOFT_TIME_LIMIT: int = 600
    BEAT_SCHEDULER: str = "django_celery_beat.schedulers:DatabaseScheduler"


class EmailConfig(Config):
    """Email configuration"""

    EMAIL_BACKEND: str = "django.core.mail.backends.console.EmailBackend"
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASSWORD: str = ""
    EMAIL_SUBJECT_PREFIX: str = ""
    DEFAULT_FROM_EMAIL: str = "root@localhost"
    SERVER_EMAIL: str = "root@localhost"


class ProjectConfig(Config):
    """Project-specific configuration"""

    OPENAI_API_KEY: str = ""
    ...


# Load configurations
django_config = DjangoConfig.load(prefix="DJANGO")
email_config = EmailConfig.load(prefix="")
project_config = ProjectConfig.load(prefix="PROJECT")
celery_config = CeleryConfig.load(prefix="CELERY")

#############################
# GENERAL
#############################
DEBUG = django_config.DEBUG
SECRET_KEY = django_config.SECRET_KEY
ALLOWED_HOSTS = django_config.ALLOWED_HOSTS

TIME_ZONE = django_config.TIME_ZONE
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [str(BASE_DIR / "locale")]

USE_X_FORWARDED_HOST = True


#############################
# DATABASES
#############################
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {"default": dj_database_url.parse(django_config.DATABASE_URL)}

# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


##############################
# STORAGES
#############################
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

#############################
# URLS
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "conf.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "wsgi.application"


#############################
# ADMIN
#############################
ADMIN_PATH = django_config.ADMIN_PATH
ADMINS = (
    [tuple(s.strip().split(":")) for s in django_config.ADMINS.split(",") if ":" in s]
    if django_config.ADMINS
    else []
)
MANAGERS = ADMINS


#############################
# APPS
#############################
INSTALLED_APPS = [
    ############################
    # Common Django apps
    ############################
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
    ############################
    # Third-party apps
    ############################
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.amazon_cognito",
    "allauth.headless",
    "allauth.usersessions",
    "corsheaders",
    "django_extensions",
    ############################
    # Local/Custom apps
    ############################
    "apps.users",
    "apps.auditlog",
    "apps.conflict_detector",
]

#############################
# AUTHENTICATION
#############################
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_USER_MODEL = django_config.AUTH_USER_MODEL
LOGIN_REDIRECT_URL = django_config.LOGIN_REDIRECT_URL
LOGIN_URL = django_config.LOGIN_URL


#############################
# PASSWORDS
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


#############################
# MIDDLEWARE
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # CSRF disabled for auth endpoints
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]


#############################
# STATIC
#############################
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(APPS_DIR / "static")] if (APPS_DIR / "static").exists() else []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


#############################
# MEDIA
#############################
MEDIA_ROOT = str(APPS_DIR / "media")
MEDIA_URL = django_config.MEDIA_URL


#############################
# TEMPLATES
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")]
        if (APPS_DIR / "templates").exists()
        else [],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"


#############################
# FIXTURES
#############################
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),) if (APPS_DIR / "fixtures").exists() else ()


#############################
# SECURITY
#############################
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = django_config.SECURE_SSL_REDIRECT
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING - CSRF disabled
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CSRF_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SECURE = bool(security_config.SECURE_SSL_REDIRECT)
# CSRF_COOKIE_NAME = "__Secure-csrftoken" if CSRF_COOKIE_SECURE else "csrftoken"


#############################
# EMAIL
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# If EMAIL_BACKEND is empty, use console backend (local development)
EMAIL_BACKEND = email_config.EMAIL_BACKEND

# Production email settings (only set when EMAIL_BACKEND is configured for SMTP)
EMAIL_HOST = email_config.EMAIL_HOST
EMAIL_PORT = email_config.EMAIL_PORT
EMAIL_USE_TLS = email_config.EMAIL_USE_TLS
EMAIL_HOST_USER = email_config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = email_config.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = email_config.DEFAULT_FROM_EMAIL
SERVER_EMAIL = email_config.SERVER_EMAIL
EMAIL_SUBJECT_PREFIX = email_config.EMAIL_SUBJECT_PREFIX
EMAIL_TIMEOUT = 5


#############################
# CACHING
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}


#############################
# LOGGING
#############################
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOG_LEVEL = django_config.LOG_LEVEL
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": LOG_LEVEL, "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

#############################
# CORS
#############################
# https://github.com/adamchainz/django-cors-headers
CORS_ALLOWED_ORIGINS = [django_config.FRONTEND_URL]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["X-Session-Token"]

# Allow cookies to be sent cross-origin
# For cross-origin requests (frontend and backend on different domains), we need:
# - SameSite=None (allows cross-origin cookies)
# - Secure=True (required when SameSite=None)
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True  # Required for SameSite=None
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True


#############################
# Celery
#############################
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_BEAT_SCHEDULER = celery_config.BEAT_SCHEDULER

CELERY_BROKER_URL = celery_config.BROKER_URL

CELERY_RESULT_BACKEND = celery_config.RESULT_BACKEND
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_SERIALIZER = "json"

CELERY_TASK_SEND_SENT_EVENT = True
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_SOFT_TIME_LIMIT = celery_config.TASK_SOFT_TIME_LIMIT
CELERY_TASK_TIME_LIMIT = celery_config.TASK_TIME_LIMIT

CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_SEND_TASK_EVENTS = True


#############################
# django-allauth
#############################
# Headless API Configuration
# https://docs.allauth.org/en/latest/headless/index.html
HEADLESS_ONLY = False

# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ALLOW_REGISTRATION = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*"]
ACCOUNT_EMAIL_VERIFICATION = "none"

SOCIALACCOUNT_ONLY = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True


#############################
# PROJECT SPECIFIC SETTINGS
#############################
PROJECT_OPENAI_API_KEY = project_config.OPENAI_API_KEY
