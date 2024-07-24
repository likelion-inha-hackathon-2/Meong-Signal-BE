from .base import *
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import json
import pymysql
import environ

pymysql.install_as_MySQLdb()

DEBUG = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
	env_file = os.path.join(BASE_DIR, '.env')
)
USER = env('DB_USER') 
NAME = env('DB_NAME') 
PASSWORD = env('DB_PASSWORD') 
HOST = env('DB_HOST') 

ALLOWED_HOSTS = ['meong-signal-back.p-e.kr', 'localhost', '127.0.0.1', 'meongsignal.kro.kr', 'meong-signal.o-r.kr', 'meong-signal.kro.kr']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": NAME,
        "USER" : USER,
        "PASSWORD" : PASSWORD,
        "HOST" : HOST,
        "PORT" : 3306,
        "OPTIONS" : {
            'init_command' : 'SET sql_mode="STRICT_TRANS_TABLES"'
        }
    }
}
