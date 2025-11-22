from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the path to the file containing the secret
_secret_key_file_path = os.getenv("DJANGO_SECRET_KEY_FILE")
if not _secret_key_file_path:
    raise Exception("DJANGO_SECRET_KEY_FILE must be a file path string")

# Read the secret from the file
_secret_key_file = open(_secret_key_file_path, "r")
SECRET_KEY = _secret_key_file.read()
_secret_key_file.close()

# Enable doing things differently if we're in debug mode
DEBUG = os.getenv("DEBUG", False) == "true"

ALLOWED_HOSTS = ["localhost"]
CSRF_TRUSTED_ORIGINS = ["http://localhost"]

# MUST NOT include protocol (e.g. "webauthn.io")
PROD_HOST_NAME = os.getenv("PROD_HOST_NAME", None)
# MUST include protocol (e.g. "https://webauthn.io")
PROD_CSRF_ORIGIN = os.getenv("PROD_CSRF_ORIGIN", None)

if PROD_HOST_NAME and PROD_CSRF_ORIGIN:
    # e.g. "webauthn.io"
    ALLOWED_HOSTS.append(PROD_HOST_NAME)
    # e.g. "https://webauthn.io"
    CSRF_TRUSTED_ORIGINS.append(PROD_CSRF_ORIGIN)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "homepage",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "webauthnio.urls"

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

WSGI_APPLICATION = "webauthnio.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "webauthnio.sqlite3",
    }
}


# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "django_default": {
            "class": "logging.StreamHandler",
        },
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["django_default"],
            "propagate": True,
        },
        "webauthnio.homepage": {
            "level": "INFO",
        },
    },
}


# Redis cache support
# https://docs.djangoproject.com/en/4.0/topics/cache/#redis-1

# This is only configurable right now to access Redis at a different hostname during testing.
# The default value is the service name when everything is running in Docker.
REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME", "redis")
REDIS_PORT = 6379
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOSTNAME}:{REDIS_PORT}/1",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = "static"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Relying party information for py_webauthn

RP_ID = os.getenv("RP_ID")
RP_NAME = os.getenv("RP_NAME")
RP_EXPECTED_ORIGIN = os.getenv("RP_EXPECTED_ORIGIN")


# .well_known/apple-app-site-association
# https://developer.apple.com/documentation/xcode/supporting-associated-domains

AASA_APP_ID_PREFIX = os.getenv("AASA_APP_ID_PREFIX")
AASA_BUNDLE_ID = os.getenv("AASA_BUNDLE_ID")
