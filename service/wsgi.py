import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
application = get_wsgi_application()
