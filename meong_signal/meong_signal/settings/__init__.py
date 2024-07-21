import os

ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'local')

if ENVIRONMENT == 'production':
    from .prod import *
else:
    from .local import *
