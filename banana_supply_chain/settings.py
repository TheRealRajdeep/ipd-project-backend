# banana_supply_chain/settings.py
import os
from pathlib import Path

# ─── BASE SETUP ────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-rci53^iw*pn-x0y1j_po+8&=ga*o@!3(v_(_rle6wm8l96&90('
DEBUG = True
ALLOWED_HOSTS = ['*']

# ─── INSTALLED APPS ────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Your apps
    'accounts',
    'shipments',
    'ml',
]

# ─── MIDDLEWARE ───────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'banana_supply_chain.urls'

# ─── TEMPLATES ────────────────────────────────────────────────────────────────

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'banana_supply_chain.wsgi.application'

# ─── DATABASES (SQLite FOR DEV) ───────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── PASSWORD VALIDATION ──────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNATIONALIZATION ─────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─── STATIC & MEDIA ──────────────────────────────────────────────────────────

STATIC_URL  = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ─── DEFAULT AUTO FIELD ──────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── REST FRAMEWORK ──────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type', 
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-credentials',
]
# ─── EMAIL (console backend for dev) ─────────────────────────────────────────

EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@example.com'

# ─── ML & MAP CONFIG ──────────────────────────────────────────────────────────

WEIGHTS_PATH        = r'C:\Users\rajde\Desktop\IPD FINAL\Backend\best.pt'
MAPPING_PATH        = r'C:\Users\rajde\Desktop\IPD FINAL\Backend\data.yaml'
GOOGLE_MAPS_API_KEY = 'AIzaSyD1NMQilodEjljGhgeFhKBDGrt4YCcMwMo'
