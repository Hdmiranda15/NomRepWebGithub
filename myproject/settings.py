from pathlib import Path
import os # Importar os para manejo de rutas de sistema

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-iyw4=6+(lfns1h2gz5*2)(t-15+p4$=hwmc7k8k^2$6=k-qv_l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Permite cualquier host durante el desarrollo.
# En producción, esto debe ser una lista de tus dominios o IPs.
ALLOWED_HOSTS = ['*'] # Cambiado a '*' para desarrollo, se puede restringir más adelante.


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion_impresion', # Tu aplicación personalizada
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Puedes agregar rutas a directorios de plantillas globales aquí si los tienes
        'APP_DIRS': True, # Busca plantillas dentro de los directorios 'templates' de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_bcnf_4fn',        # Tu nombre de base de datos
        'USER': 'h-debian',           # Tu usuario de base de datos
        'PASSWORD': '12345',          # Tu contraseña de base de datos
        'HOST': 'localhost',          # O tu host de DB (e.g., '127.0.0.1')
        'PORT': '5432',               # Puerto predeterminado de PostgreSQL
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-mx' # Puedes cambiar a 'es-mx' para español de México, o 'es-es' etc.

TIME_ZONE = 'America/Mexico_City' # Ajusta tu zona horaria real, ej. 'America/Mexico_City', 'America/Bogota', 'America/Buenos_Aires'

USE_I18N = True # Habilita la internacionalización

USE_TZ = True # Habilita el soporte para zonas horarias


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# Define STATIC_ROOT para el comando collectstatic en producción
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files (User-uploaded files)
# Archivos subidos por los usuarios, como los documentos DOCX
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de mensajes (opcional, para controlar cómo se muestran los mensajes de Django)
# from django.contrib.messages import constants as messages
# MESSAGE_TAGS = {
#     messages.DEBUG: 'debug',
#     messages.INFO: 'info',
#     messages.SUCCESS: 'success',
#     messages.WARNING: 'warning',
#     messages.ERROR: 'danger',
# }
