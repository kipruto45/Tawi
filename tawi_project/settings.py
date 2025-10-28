import os
from pathlib import Path
import secrets
import sys
from django.core.exceptions import ImproperlyConfigured

# Load local .env early so development env vars like USE_ALLAUTH, GOOGLE_CLIENT_ID
# and GOOGLE_SECRET are available during local runs. This is best-effort and
# will not crash if python-dotenv isn't installed.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

_env_secret = os.environ.get('SECRET_KEY')
# If a SECRET_KEY is not provided, generate a long development key when
# DEBUG is True so local checks won't raise the short-key warning. In
# production (DEBUG=False) require the env var to be set to a secure value.
if _env_secret:
    SECRET_KEY = _env_secret
else:
    # generate a reasonably strong temporary key for local development/test
    SECRET_KEY = secrets.token_urlsafe(64)

# Toggle DEBUG via environment in production. Default to True for local development.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') in ('1', 'true', 'True')

# Allow configuring allowed hosts via environment. Provide sensible defaults for dev.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.localhost,127.0.0.1,testserver').split(',')

# When running locally (DEBUG=True) ensure the Django test client and simple
# scripts can use the default test host 'testserver' even if the developer's
# .env overrides ALLOWED_HOSTS. This prevents DisallowedHost errors in
# quick smoke checks and scripts that use the test client.
if DEBUG and 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',

    # apps
    'accounts',
    'beneficiaries',
    'trees',
    'monitoring',
    'reports',
    'notifications',
    'qrcodes',
    'media_app',
    'donations',
    'dashboard',
    'core',
    'feedback',
    'events',
]

# Use custom user model
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'core.middleware.EnsureUserMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Try to enable WhiteNoise if it's installed in the environment. We do this
# dynamically so local development without the package doesn't crash on import.
try:
    import importlib
    importlib.import_module('whitenoise')
    wn_mw = 'whitenoise.middleware.WhiteNoiseMiddleware'
    if wn_mw not in MIDDLEWARE:
        try:
            idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
            MIDDLEWARE.insert(idx + 1, wn_mw)
        except ValueError:
            MIDDLEWARE.insert(0, wn_mw)
except Exception:
    # WhiteNoise not installed; skip hooking it in.
    pass

# Detect test runs and relax strict security redirects during tests so that
# API tests which POST to HTTP endpoints don't get redirected to HTTPS and
# fail with 301. We don't change DEBUG here; we only disable forced
# HTTPS/secure cookie enforcement for test runs.
# `sys` is imported at the top of this file.
if any('test' in a for a in sys.argv):
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

ROOT_URLCONF = 'tawi_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notifications_context',
                'core.context_processors.user_profile',
                'core.context_processors.admin_flag',
            ],
            'builtins': [
                'accounts.templatetags.social_tags',
                'core.templatetags.test_filters',
            ],
        },
    },
]

WSGI_APPLICATION = 'tawi_project.wsgi.application'

# Default database: PostgreSQL (project default). You may override via
# DATABASE_URL or the USE_POSTGRES/POSTGRES_* environment variables.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'tawi_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
    'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'rop45'),
        'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Include the top-level project `static/` directory so files placed in
# `BASE_DIR/static/...` are discoverable by Django's staticfiles during
# development without needing to collectstatic.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise: enable compressed static file serving and manifest caching when
# running with collectstatic in production. Requires whitenoise in requirements.
WHITENOISE_AUTOREFRESH = DEBUG
STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', 'whitenoise.storage.CompressedManifestStaticFilesStorage' if not DEBUG else 'django.contrib.staticfiles.storage.StaticFilesStorage')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        # for production consider: 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
    }
}

# Use a custom test runner that ensures unittest discovery uses the project
# root as the top_level_dir so apps' `tests` packages are properly qualified
# (avoids ambiguous `tests.*` module names during discovery).
TEST_RUNNER = 'tawi_project.test_runner.CustomDiscoverRunner'

# Simple JWT settings (optional - install djangorestframework-simplejwt to use)
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_ALL_ORIGINS = True

# Simple in-memory cache for development. For production use Redis or Memcached.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Celery settings (use Redis in production)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)

# Email backend for dev: console. Configure SMTP in production.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
# Default sender for outgoing emails from the project
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'tawiproject@gmail.com')
# Server email (used as the sender for error emails and other system messages)
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'tawiproject@gmail.com')

# Example Celery beat schedule (enable in production settings or via django-celery-beat)
# Import crontab lazily so missing celery in local/dev doesn't break settings import.
try:
    from celery.schedules import crontab
except Exception:
    crontab = None

if crontab is not None:
    CELERY_BEAT_SCHEDULE = {
        'remind-missing-updates-daily': {
            'task': 'trees.tasks.remind_missing_updates',
            'schedule': crontab(hour=7, minute=0),
            'args': (30,)
        }
    }

# Basic logging configuration - expand in production to use file handlers or external logging services
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Add a specific logger for accounts login redirects for auditing
LOGGING['loggers'] = {
    'accounts.login': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    }
}

# Logger for role changes audit trail
LOGGING['loggers']['accounts.role_changes'] = {
    'handlers': ['console'],
    'level': 'INFO',
    'propagate': False,
}

# Optional S3 settings: enable by setting USE_S3=1 and providing AWS_* env vars
USE_S3 = os.environ.get('USE_S3') in ('1', 'true', 'True')
if USE_S3:
    INSTALLED_APPS += ['storages']
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', None)
    AWS_QUERYSTRING_AUTH = False

# Branding defaults used in report generation
ORG_NAME = os.environ.get('ORG_NAME', 'Tawi Tree Planting')
ORG_TAGLINE = os.environ.get('ORG_TAGLINE', 'Growing communities, one tree at a time')

# Optional authentication extensions (enable via env vars)
USE_ALLAUTH = os.environ.get('USE_ALLAUTH') in ('1', 'true', 'True')
USE_AXES = os.environ.get('USE_AXES') in ('1', 'true', 'True')
USE_2FA = os.environ.get('USE_2FA') in ('1', 'true', 'True')

if USE_ALLAUTH:
    INSTALLED_APPS += [
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
        # auth REST helpers
        'rest_framework.authtoken',
        'dj_rest_auth',
        'dj_rest_auth.registration',
    ]
    # allauth requires AccountMiddleware for some flows; ensure it's present
    try:
        mw = 'allauth.account.middleware.AccountMiddleware'
        if mw not in MIDDLEWARE:
            # insert after AuthenticationMiddleware if present, otherwise append
            try:
                idx = MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware')
                MIDDLEWARE.insert(idx + 1, mw)
            except ValueError:
                MIDDLEWARE.append(mw)
    except Exception:
        # best-effort: if anything goes wrong, don't crash settings import
        pass
    SITE_ID = int(os.environ.get('SITE_ID', 1))
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]
    # Basic allauth settings useful for local development. Set USE_ALLAUTH=1
    # and provide GOOGLE_CLIENT_ID and GOOGLE_SECRET in the environment to enable.
    ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'optional')
    # New django-allauth configuration: prefer ACCOUNT_LOGIN_METHODS and
    # ACCOUNT_SIGNUP_FIELDS. Older env vars (ACCOUNT_AUTHENTICATION_METHOD,
    # ACCOUNT_EMAIL_REQUIRED) are still supported for convenience but we map
    # them to the new settings to avoid deprecation warnings.
    _auth_method = os.environ.get('ACCOUNT_AUTHENTICATION_METHOD', 'username_email')
    # Map legacy string to the new ACCOUNT_LOGIN_METHODS set expected by
    # recent allauth versions.
    if _auth_method in ('username',):
        ACCOUNT_LOGIN_METHODS = {'username'}
    elif _auth_method in ('email',):
        ACCOUNT_LOGIN_METHODS = {'email'}
    else:
        # default: allow both username and email login
        ACCOUNT_LOGIN_METHODS = {'username', 'email'}

    # Map legacy ACCOUNT_EMAIL_REQUIRED to ACCOUNT_SIGNUP_FIELDS. If the
    # environment explicitly sets ACCOUNT_SIGNUP_FIELDS we prefer that value.
    _signup_fields_env = os.environ.get('ACCOUNT_SIGNUP_FIELDS')
    if _signup_fields_env:
        # allow comma-separated override in env
        ACCOUNT_SIGNUP_FIELDS = [f.strip() for f in _signup_fields_env.split(',') if f.strip()]
    else:
        _email_required = os.environ.get('ACCOUNT_EMAIL_REQUIRED', '1') in ('1', 'true', 'True')
        if _email_required:
            ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
        else:
            ACCOUNT_SIGNUP_FIELDS = ['email', 'username*', 'password1*', 'password2*']

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': ['profile', 'email'],
            'AUTH_PARAMS': {'access_type': 'online'},
            # Recommended: use OAUTH_PKCE = True for modern clients
            'OAUTH_PKCE_ENABLED': True,
        }
    }

if USE_AXES:
    INSTALLED_APPS += ['axes']
    MIDDLEWARE.insert(0, 'axes.middleware.AxesMiddleware')
    AXES_FAILURE_LIMIT = int(os.environ.get('AXES_FAILURE_LIMIT', 5))
    AXES_COOLOFF_TIME = int(os.environ.get('AXES_COOLOFF_TIME', 1))  # hours
    AXES_LOCK_OUT_AT_FAILURE = True

if USE_2FA:
    INSTALLED_APPS += [
        'django_otp',
        'django_otp.plugins.otp_totp',
        'django_otp.plugins.otp_email',
        'django_otp.plugins.otp_static',
        'two_factor',
        'two_factor.plugins.email',
    ]
    MIDDLEWARE.insert(0, 'django_otp.middleware.OTPMiddleware')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Remember-me session expiry (seconds). Default: 2 weeks
LOGIN_REMEMBER_SECONDS = int(os.environ.get('LOGIN_REMEMBER_SECONDS', 1209600))

# Central post-login redirect. Point Django's LOGIN_REDIRECT_URL to the
# `accounts:post_login_redirect` view so all login flows (including social/allauth)
# land on a single deterministic endpoint which will route users based on role.
LOGIN_REDIRECT_URL = 'accounts:post_login_redirect'

# CORS/CSRF notes: in development we allow all origins; in production set CORS_ALLOWED_ORIGINS via env var
if os.environ.get('CORS_ALLOWED_ORIGINS'):
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS').split(',')

# Database: production-ready template (uncomment and configure to use PostgreSQL/MySQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_DB', 'tawi_db'),
#         'USER': os.environ.get('POSTGRES_USER', 'tawi_user'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
#         'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
#         'PORT': os.environ.get('POSTGRES_PORT', '5432'),
#     }
# }

# If DATABASE_URL is provided (e.g., by Render), parse it and configure the DB.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
    except Exception:
        # Fall back to lightweight parsing when dj-database-url isn't available
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        engine = 'django.db.backends.postgresql'
        if parsed.scheme.startswith('postgres') or parsed.scheme.startswith('postgresql'):
            engine = 'django.db.backends.postgresql'
        elif parsed.scheme.startswith('mysql'):
            engine = 'django.db.backends.mysql'
        DATABASES = {
            'default': {
                'ENGINE': engine,
                'NAME': parsed.path.lstrip('/'),
                'USER': parsed.username,
                'PASSWORD': parsed.password,
                'HOST': parsed.hostname,
                'PORT': parsed.port or '',
            }
        }

# Security settings that should be enabled in production
if not DEBUG:
    # If you're behind a proxy/load-balancer (Render provides TLS), enable this
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Only enable SECURE_SSL_REDIRECT when explicitly requested via environment.
    # Tests run with DEBUG=False; don't force HTTPS in that environment unless
    # the deploy configuration sets SECURE_SSL_REDIRECT=1/true.
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') in ('1', 'true', 'True')
    # HSTS (enable cautiously; once set, browsers will enforce HTTPS)
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 60))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True') in ('1', 'true', 'True')
    SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False') in ('1', 'true', 'True')

    # ---------------------------------------------------------------------------
    # Deployment environment block - load .env for local dev and read production
    # settings from the environment. Uses python-dotenv to make local development
    # similar to production while avoiding committing secrets.
    # ---------------------------------------------------------------------------
    try:
        # Load .env when present (no-op if python-dotenv isn't installed).
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / '.env')
    except Exception:
        # python-dotenv not installed or .env not present; continue using os.environ
        pass

    # Re-read SECRET_KEY/DEBUG/ALLOWED_HOSTS in case they were provided via .env
    SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
    DEBUG = os.environ.get('DJANGO_DEBUG', 'False' if not DEBUG else 'True') in ('1', 'true', 'True')
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', ','.join(ALLOWED_HOSTS)).split(',')

    # In production require a sufficiently strong SECRET_KEY to avoid weak-key
    # security warnings. Developers should set SECRET_KEY in the environment
    # to a long, random value (recommended >=50 chars). We raise an explicit
    # error here to prevent accidental insecure deployments.
    if not DEBUG:
        if not SECRET_KEY or len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5:
            raise ImproperlyConfigured(
                'SECRET_KEY is not set to a secure value. Set the SECRET_KEY env var to a long, random string (>=50 chars) for production.'
            )

    # If running on Render or another platform that provides DATABASE_URL, prefer it
    DATABASE_URL = os.environ.get('DATABASE_URL', DATABASE_URL)
    if DATABASE_URL:
        try:
            import dj_database_url
            DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
        except Exception:
            # keep the lighter fallback parsing above
            pass

    # Allow forcing PostgreSQL as the project's database via USE_POSTGRES.
    # This is useful for local development parity with CI. When set, we prefer
    # explicit POSTGRES_* env vars (use sensible defaults that match CI services).
    if os.environ.get('USE_POSTGRES') in ('1', 'true', 'True') and not DATABASE_URL:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
                'USER': os.environ.get('POSTGRES_USER', 'postgres'),
                'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
                'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
                'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            }
        }

# Optional: allow overriding the test database name to make local test runs
# predictable and avoid Django's automatic 'test_' prefixing issues. Setting
# DJANGO_TEST_DB_NAME will set DATABASES['default']['TEST']['NAME'] directly
# so the test runner will reuse or create the specified database name.
DJANGO_TEST_DB_NAME = os.environ.get('DJANGO_TEST_DB_NAME')
if DJANGO_TEST_DB_NAME:
    DATABASES.setdefault('default', {})
    DATABASES['default'].setdefault('TEST', {})
    DATABASES['default']['TEST']['NAME'] = DJANGO_TEST_DB_NAME

    # Configure static files storage: use WhiteNoise storage in production when
    # available and DEBUG is False. Users can override STATICFILES_STORAGE via env.
    if not DEBUG:
        STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', 'whitenoise.storage.CompressedManifestStaticFilesStorage')

# When running under the test runner, some deployment security settings
# (like SECURE_SSL_REDIRECT) may be enabled via environment. Those cause
# API endpoints to redirect to HTTPS (301) and break API tests expecting
# 200/201 responses. Ensure we relax forced HTTPS for test runs here.
if any('test' in a for a in sys.argv):
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Ensure a non-empty SECRET_KEY during tests (some developers keep SECRET_KEY
# blank in .env; tests require a signing key). Use a safe development value
# only for the test run and do not persist it to the environment.
if any('test' in a for a in sys.argv) and not SECRET_KEY:
    SECRET_KEY = 'test-secret-key-for-local-runs'

# Make sure the test host used by Django's test client is allowed when running
# tests (even when DEBUG=False). This prevents DisallowedHost errors during
# unit tests and smoke scripts that call the test client directly.
if any('test' in a for a in sys.argv):
    try:
        # ALLOWED_HOSTS may be a list or a string split earlier; coerce to list
        if isinstance(ALLOWED_HOSTS, str):
            ALLOWED_HOSTS = ALLOWED_HOSTS.split(',')
    except NameError:
        ALLOWED_HOSTS = []
    if 'testserver' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('testserver')

