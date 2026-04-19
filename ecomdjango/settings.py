from pathlib import Path
from decouple import config, Csv
from dj_database_url import parse as db_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("DJANGO_SECRET")
# By-default decouple return variables in string format
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=[], cast=Csv())


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'anymail',
    
    'allauth',
    'allauth.usersessions',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'users',
    'core',
    'product',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'ecomdjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecomdjango.wsgi.application'

DATABASES = {
    "default": config('DATABASE_URL', cast=db_url)
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_DIRS = [BASE_DIR/"static"]

# anymail config
EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_PROVIDER_NAME = config("EMAIL_PROVIDER_NAME").upper()
ANYMAIL = {
    f"{EMAIL_PROVIDER_NAME}_API_KEY": config("EMAIL_API_KEY"),
}
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# allauth config
ACCOUNT_SIGNUP_FIELDS = [ "email*", "password1*", "password2*" ]
ACCOUNT_SIGNUP_FORM_CLASS = "users.forms.UserSignUpForm"
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_MAX_EMAIL_ADDRESSES = 1

# allauth social account providers config
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "EMAIL_AUTHENTICATION": True,
        "APPS": [
            {
                "client_id": config("GOOGLE_CLIENT_ID"),
                "secret": config("GOOGLE_CLIENT_SECRET"),
                "key": "",
                "settings": {
                    "scope": [
                        "profile",
                        "email",
                    ],
                    "auth_params": {
                        "access_type": "online",
                    },
                },
            },
        ],
    }
}