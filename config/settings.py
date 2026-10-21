"""Réglages du site de l'ASBL Yeba (Django + Wagtail).

Les valeurs propres au serveur (secrets, domaine, e-mail, base) sont lues dans .env : voir .env.exemple.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _charger_env(fichier):
    """Lit .env (lignes NOM=valeur) s'il existe. Une variable déjà définie dans l'environnement garde la priorité."""
    if not fichier.exists():
        return
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        nom, valeur = ligne.split("=", 1)
        os.environ.setdefault(nom.strip(), valeur.strip().strip('"').strip("'"))


_charger_env(BASE_DIR / ".env")


def env(nom, defaut=""):
    return os.environ.get(nom, defaut)


def env_bool(nom, defaut=False):
    return env(nom, "1" if defaut else "0").lower() in ("1", "true", "oui", "yes")


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-uniquement-a-remplacer-en-production")
DEBUG = env_bool("DJANGO_DEBUG", True)
if not DEBUG and SECRET_KEY.startswith("dev-"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY doit être défini en production (voir .env.exemple).")

ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")]
SITE_URL = env("DJANGO_SITE_URL", "http://localhost:8000" if DEBUG else f"https://{ALLOWED_HOSTS[0]}").rstrip("/")

INSTALLED_APPS = [
    "site_yeba",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django_filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]
if env_bool("DJANGO_GZIP", True):
    MIDDLEWARE.insert(1, "django.middleware.gzip.GZipMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if env("DJANGO_DB_ENGINE", "sqlite") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DJANGO_DB_NAME", "yeba"),
            "USER": env("DJANGO_DB_USER", "yeba"),
            "PASSWORD": env("DJANGO_DB_PASSWORD"),
            "HOST": env("DJANGO_DB_HOST", "localhost"),
            "PORT": env("DJANGO_DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": env("DJANGO_DB_NAME", str(BASE_DIR / "db.sqlite3")),
            "OPTIONS": {"timeout": 20},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if DEBUG else
                    "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Sessions de deux semaines ; cookies sécurisés en production.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG

# Production derrière le proxy HTTPS d'Opalstack.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
# L'aperçu des pages dans l'éditeur Wagtail s'affiche dans un cadre du même site.
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = 0 if DEBUG else int(env("DJANGO_HSTS_SECONDS", "3600"))
# W019 : SAMEORIGIN voulu (aperçu Wagtail) ; W005 et W021 : sous-domaines et préchargement HSTS non activés.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W019", "security.W021"] + ([] if SECURE_SSL_REDIRECT else ["security.W008"])

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"} if DEBUG else
               {"BACKEND": "django.core.cache.backends.filebased.FileBasedCache", "LOCATION": BASE_DIR / ".cache"},
}

# E-mails : affichés dans la console tant que DJANGO_EMAIL_HOST est vide (développement), sinon envoyés par SMTP.
EMAIL_HOST = env("DJANGO_EMAIL_HOST")
EMAIL_BACKEND = ("django.core.mail.backends.smtp.EmailBackend" if EMAIL_HOST
                 else "django.core.mail.backends.console.EmailBackend")
EMAIL_PORT = int(env("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("DJANGO_EMAIL_USER")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_PASSWORD")
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_TLS", EMAIL_PORT == 587)
EMAIL_USE_SSL = env_bool("DJANGO_EMAIL_SSL", EMAIL_PORT == 465)
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = env("DJANGO_EMAIL_FROM", "Yeba <ne-pas-repondre@yeba.cd>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [(a.strip(), a.strip()) for a in env("DJANGO_ADMINS").split(",") if a.strip()]
EMAIL_SUBJECT_PREFIX = "[Yeba] "

# Journaux : erreurs dans logs/django.log (rotation à 5 Mo) et par e-mail aux ADMINS en production.
(BASE_DIR / "logs").mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "{asctime} {levelname} {name} : {message}", "style": "{"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "fichier": {"class": "logging.handlers.RotatingFileHandler", "filename": BASE_DIR / "logs" / "django.log",
                    "maxBytes": 5 * 1024 * 1024, "backupCount": 5, "formatter": "simple", "level": "WARNING",
                    "encoding": "utf-8"},
        "mail_admins": {"class": "django.utils.log.AdminEmailHandler", "level": "ERROR",
                        "filters": ["require_debug_false"]},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "root": {"handlers": ["console", "fichier"], "level": "INFO" if DEBUG else "WARNING"},
    "loggers": {
        "django.request": {"handlers": ["fichier", "mail_admins"], "level": "ERROR", "propagate": False},
        # Wagtail note chaque tâche de fond (index de recherche, références) : bruit inutile dans la console.
        "django_tasks": {"level": "WARNING"},
        "wagtail": {"level": "WARNING"},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024

# Wagtail : l'outil d'édition du site, en français.
WAGTAIL_SITE_NAME = "Yeba"
WAGTAILADMIN_BASE_URL = SITE_URL
WAGTAIL_I18N_ENABLED = False
WAGTAILADMIN_PERMITTED_LANGUAGES = [("fr", "Français"), ("en", "English")]
WAGTAILSEARCH_BACKENDS = {"default": {"BACKEND": "wagtail.search.backends.database"}}
WAGTAILDOCS_EXTENSIONS = ["csv", "docx", "odt", "pdf", "pptx", "txt", "xlsx", "zip"]
WAGTAILDOCS_MAX_UPLOAD_SIZE = 20 * 1024 * 1024
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp"]
# Pas de vérification des nouvelles versions de Wagtail depuis l'administration (les mises à jour passent par requirements.txt).
WAGTAIL_ENABLE_UPDATE_CHECK = False
# Pas d'avatars Gravatar dans l'administration (requête vers un service extérieur à chaque page).
WAGTAIL_GRAVATAR_PROVIDER_URL = None
