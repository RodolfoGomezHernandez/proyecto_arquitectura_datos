import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arquitecturadatos.settings')
django.setup()

from ventas.utils import load_csv_data, save_fact_ventas
from ventas.models import FactVenta

with open('sample_ventas.csv', 'rb') as f:
    processed, summary = load_csv_data(f)
    print('summary:', summary)
    saved = save_fact_ventas(processed)
    print('saved', len(saved))
    print('db count', FactVenta.objects.count())
