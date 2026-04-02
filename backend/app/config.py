import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SECRET_KEY = os.getenv("SECRET_KEY", "05b40fa355e34ed9ed947c843607baa44339ac1f2af4c019")
DEBUG = True

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'LaunchPad.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "salty-dev-salt")
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
SECURITY_TOKEN_MAX_AGE = 86400  # 24 hours
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True
WTF_CSRF_ENABLED = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")
CACHE_REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
CACHE_REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_DEFAULT_TIMEOUT = 300
MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
MAIL_PORT = int(os.getenv("MAIL_PORT", 1025))
MAIL_DEFAULT_SENDER = "placement@LaunchPad.com"

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
