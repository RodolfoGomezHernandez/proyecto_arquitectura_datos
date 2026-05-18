from datetime import date
from django.contrib import messages
from django.db import DatabaseError
from django.db.models import Sum
from django.shortcuts import redirect, render
from .forms import UploadCSVForm
from .models import FactVenta
from .utils import load_csv_data, save_fact_ventas

SESSION_PENDING_VALID_ROWS = 'pending_valid_rows'
SESSION_PENDING_COUNT = 'pending_valid_count'
SESSION_LAST_TOTAL = 'last_total_processed'
SESSION_LAST_VALID = 'last_valid_processed'
SESSION_LAST_CORRECTED = 'last_corrected_processed'
SESSION_LAST_ERRORS = 'last_errors_processed'


def _serialize_valid_rows(rows):
    serialized = []
    for row in rows:
        data = row['data'].copy()
        fecha = data.get('fecha')
        data['fecha'] = fecha.isoformat() if isinstance(fecha, date) else None
        serialized.append(data)
    return serialized


def _deserialize_valid_rows(rows):
    restored = []
    for row in rows:
        data = row.copy()
        fecha = data.get('fecha')
        data['fecha'] = date.fromisoformat(fecha) if fecha else None
        restored.append({
            'data': data,
            'valido': True,
            'errors': '',
        })
    return restored


def inicio(request):
    summary = None
    details = []
    csv_columns = []
    pending_valid_count = request.session.get(SESSION_PENDING_COUNT, 0)
    form = UploadCSVForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'subir_limpio':
            pending_rows = request.session.get(SESSION_PENDING_VALID_ROWS, [])
            if not pending_rows:
                messages.error(request, 'No hay datos limpios pendientes para subir.')
                return redirect('ventas:inicio')

            clean_rows = _deserialize_valid_rows(pending_rows)
            try:
                FactVenta.objects.all().delete()
                save_fact_ventas(clean_rows)
                request.session.pop(SESSION_PENDING_VALID_ROWS, None)
                request.session.pop(SESSION_PENDING_COUNT, None)
                messages.success(request, 'Carga finalizada: se limpio la tabla y se subieron solo filas validas.')
            except DatabaseError:
                messages.error(request, 'Error al guardar datos en la base local.')
            return redirect('ventas:inicio')

        form = UploadCSVForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, 'Por favor seleccione un archivo CSV valido.')
        else:
            csv_file = form.cleaned_data['csv_file']
            try:
                processed, summary, csv_columns = load_csv_data(csv_file.file)
                details = processed[:100]
                valid_rows = [row for row in processed if row['valido']]
                corrected_count = summary['total'] - summary['validos']
                request.session[SESSION_PENDING_VALID_ROWS] = _serialize_valid_rows(valid_rows)
                request.session[SESSION_PENDING_COUNT] = len(valid_rows)
                request.session[SESSION_LAST_TOTAL] = summary['total']
                request.session[SESSION_LAST_VALID] = summary['validos']
                request.session[SESSION_LAST_CORRECTED] = corrected_count
                request.session[SESSION_LAST_ERRORS] = summary['errores']
                request.session.modified = True
                pending_valid_count = len(valid_rows)
                messages.success(request, 'Analisis completado. Revisa errores y luego usa "Subir a BD local".')
            except ValueError as exc:
                messages.error(request, str(exc))
            except DatabaseError:
                messages.error(request, 'Error al procesar datos en memoria.')

    return render(request, 'ventas/inicio.html', {
        'form': form,
        'summary': summary,
        'details': details,
        'csv_columns': csv_columns,
        'pending_valid_count': pending_valid_count,
    })


def tablero(request):
    clean_total = FactVenta.objects.count()
    processed_total = request.session.get(SESSION_LAST_TOTAL, clean_total)
    processed_valid = request.session.get(SESSION_LAST_VALID, clean_total)
    processed_corrected = request.session.get(SESSION_LAST_CORRECTED, 0)
    processed_errors = request.session.get(SESSION_LAST_ERRORS, 0)
    porcentaje_validos = round((processed_valid / processed_total * 100), 2) if processed_total else 0
    porcentaje_corregidos = round((processed_corrected / processed_total * 100), 2) if processed_total else 0
    ventas_por_categoria = list(
        FactVenta.objects
        .values('categoria')
        .annotate(total_monto=Sum('monto'), total_cantidad=Sum('cantidad'))
        .order_by('-total_monto')
    )
    ventas_por_mes = list(
        FactVenta.objects
        .exclude(fecha__isnull=True)
        .values('fecha__month')
        .annotate(total_monto=Sum('monto'), total_cantidad=Sum('cantidad'))
        .order_by('fecha__month')
    )
    categoria_labels = [(item['categoria'] or 'Sin categoria') for item in ventas_por_categoria]
    categoria_values = [float(item['total_monto'] or 0) for item in ventas_por_categoria]
    mes_labels = [f"Mes {item['fecha__month']}" for item in ventas_por_mes]
    mes_values = [float(item['total_monto'] or 0) for item in ventas_por_mes]
    clean_rows = FactVenta.objects.order_by('-creado')[:100]

    return render(request, 'ventas/tablero.html', {
        'total_procesados': processed_total,
        'validos_procesados': processed_valid,
        'corregidos_procesados': processed_corrected,
        'errores_detectados': processed_errors,
        'total_limpios_bd': clean_total,
        'porcentaje_validos': porcentaje_validos,
        'porcentaje_corregidos': porcentaje_corregidos,
        'ventas_por_categoria': ventas_por_categoria,
        'ventas_por_mes': ventas_por_mes,
        'categoria_labels': categoria_labels,
        'categoria_values': categoria_values,
        'mes_labels': mes_labels,
        'mes_values': mes_values,
        'clean_rows': clean_rows,
    })
