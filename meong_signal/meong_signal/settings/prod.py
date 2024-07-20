from .base import *
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import json
import pymysql

pymysql.install_as_MySQLdb()

DEBUG = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent

secret_file = BASE_DIR / 'secrets.json'

with open(secret_file) as file:
    secrets = json.loads(file.read())

def get_secret(setting,secrets_dict = secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

USER = get_secret('USER') 
NAME = get_secret('NAME') 
PASSWORD = get_secret('PASSWORD') 
HOST = get_secret('HOST') 

ALLOWED_HOSTS = ['meong-signal-back.p-e.kr', 'localhost', '127.0.0.1',]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": NAME,
        "USER" : USER,
        "PASSWORD" : PASSWORD,
        "HOST" : HOST,
        "PORT" : 3306,
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR,'static')