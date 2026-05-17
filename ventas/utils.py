import csv
import io
from datetime import datetime
from .models import FactVenta

EXPECTED_COLUMNS = [
    'cliente',
    'email',
    'region',
    'producto',
    'categoria',
    'marca',
    'tienda',
    'ciudad',
    'tipo_tienda',
    'fecha',
    'cantidad',
    'monto',
]


def normalize_text(value):
    if not isinstance(value, str):
        return ''
    return value.strip().title()


def validate_email(value):
    return isinstance(value, str) and '@' in value and '.' in value


def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def parse_decimal(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)
    except (ValueError, TypeError, AttributeError):
        return None


def parse_fecha(value):
    if not value:
        return None

    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def validate_and_transform_row(row):
    errors = []
    data = {}

    for column in EXPECTED_COLUMNS:
        data[column] = (row.get(column, '') or '').strip()

    if not data['cliente']:
        errors.append('cliente vacío')
    if not validate_email(data['email']):
        errors.append('email inválido')
    if not data['categoria']:
        errors.append('categoria vacía')

    fecha = parse_fecha(data['fecha'])
    if fecha is None:
        errors.append('fecha inválida')

    cantidad = parse_int(data['cantidad'])
    if cantidad is None or cantidad < 0:
        errors.append('cantidad inválida')

    monto = parse_decimal(data['monto'])
    if monto is None or monto < 0:
        errors.append('monto inválido')

    data['fecha'] = fecha
    data['cantidad'] = cantidad or 0
    data['monto'] = monto or 0.0
    data['cliente'] = normalize_text(data['cliente'])
    data['producto'] = normalize_text(data['producto'])
    data['categoria'] = normalize_text(data['categoria'])
    data['marca'] = normalize_text(data['marca'])
    data['tienda'] = normalize_text(data['tienda'])
    data['ciudad'] = normalize_text(data['ciudad'])
    data['tipo_tienda'] = normalize_text(data['tipo_tienda'])
    data['region'] = normalize_text(data['region'])

    valido = len(errors) == 0

    return data, valido, errors


def load_csv_data(file_obj):
    decoded = io.TextIOWrapper(file_obj, encoding='utf-8')
    reader = csv.DictReader(decoded)
    headers = [h.strip() for h in reader.fieldnames or []]

    if headers != EXPECTED_COLUMNS:
        raise ValueError('Las columnas del CSV no coinciden con el formato esperado.')

    processed = []
    seen = set()

    for row in reader:
        row_key = tuple((row.get(col, '') or '').strip() for col in EXPECTED_COLUMNS)
        if row_key in seen:
            continue
        seen.add(row_key)

        data, valido, errors = validate_and_transform_row(row)
        processed.append({
            'data': data,
            'valido': valido,
            'errors': '; '.join(errors),
        })

    summary = {
        'total': len(processed),
        'validos': sum(1 for item in processed if item['valido']),
        'errores': sum(1 for item in processed if item['errors']),
    }

    return processed, summary


def save_fact_ventas(processed_rows):
    saved_rows = []
    for row in processed_rows:
        data = row['data']
        saved_rows.append(
            FactVenta.objects.create(
                cliente=data['cliente'],
                email=data['email'],
                region=data['region'],
                producto=data['producto'],
                categoria=data['categoria'],
                marca=data['marca'],
                tienda=data['tienda'],
                ciudad=data['ciudad'],
                tipo_tienda=data['tipo_tienda'],
                fecha=data['fecha'],
                cantidad=data['cantidad'],
                monto=data['monto'],
                valido=row['valido'],
                errores=row['errors'],
            )
        )
    return saved_rows
