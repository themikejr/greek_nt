"""
Django settings for greek_nt project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-c40@%2cl+u#b-62#4_d)x*@mi#+(u-_er9_i(00unpp(si=0_6"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Update ALLOWED_HOSTS setting
ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "gnt.mikebrinker.net,www.gnt.mikebrinker.net,greek-nt.fly.dev,localhost,0.0.0.0",
).split(",")
CSRF_TRUSTED_ORIGINS = [
    "https://greek-nt.fly.dev",
    "https://gnt.mikebrinker.net",
    "https://www.gnt.mikebrinker.net",
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "greek_nt",
    "tailwind",
    "theme",
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

ROOT_URLCONF = "greek_nt.urls"

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

WSGI_APPLICATION = "greek_nt.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql"
#         if os.getenv("ENVIRONMENT") == "production"
#         else "django.db.backends.sqlite3",
#         "NAME": os.getenv("SUPABASE_DB_NAME", BASE_DIR / "db.sqlite3"),
#         "USER": os.getenv("SUPABASE_DB_USER"),
#         "PASSWORD": os.getenv("SUPABASE_DB_PASSWORD"),
#         "HOST": os.getenv("SUPABASE_DB_HOST"),
#         "PORT": os.getenv("SUPABASE_DB_PORT", "5432"),
#         "OPTIONS": {"sslmode": "require"}
#         if os.getenv("ENVIRONMENT") == "production"
#         else {},
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3"
        if os.getenv("ENVIRONMENT") != "production"
        else "django.db.backends.postgresql",
        "NAME": BASE_DIR / "db.sqlite3"
        if os.getenv("ENVIRONMENT") != "production"
        else "postgres",
        "OPTIONS": {
            "service": None,
        },
        "DATABASE_URL": f"postgres://postgres:{os.getenv('SUPABASE_DB_PASSWORD')}@db.gcetotafalmnyfhuuvch.supabase.co:5432/postgres?sslmode=require"
        if os.getenv("ENVIRONMENT") == "production"
        else None,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "greek_nt_cache",
        "TIMEOUT": 86400,  # 24 hours
    }
    if ENVIRONMENT == "production"
    else {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TAILWIND_APP_NAME = "theme"

# For Fly.io Hosting
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "theme" / "static",
]
