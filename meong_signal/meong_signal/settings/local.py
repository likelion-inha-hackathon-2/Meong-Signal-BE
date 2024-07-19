from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# s3
AWS_ACCESS_KEY_ID = get_secret('AWS_LOCAL_ACCESS_KEY_ID') 
AWS_SECRET_ACCESS_KEY = get_secret('AWS_LOCAL_SECRET_ACCESS_KEY')
AWS_REGION = 'ap-northeast-2'

###S3 Storages
AWS_STORAGE_BUCKET_NAME = get_secret('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME,AWS_REGION)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# MEDIA_ROOT = os.path.join(BASE_DIR, 'path/to/store/my/files/')