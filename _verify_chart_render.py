import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ArquitecturaDatos.settings')
import django

django.setup()

from django.conf import settings
from django.test import Client

settings.ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

c = Client()
r = c.get('/panel/')
h = r.content.decode('utf-8', errors='ignore')

print('STATUS', r.status_code)
print('HAS_JSON_SCRIPT', ('categoria-labels-data' in h and 'mes-values-data' in h))
print('HAS_CANVAS', ('id="categoriaChart"' in h and 'id="mesChart"' in h))
