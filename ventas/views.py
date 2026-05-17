from django.shortcuts import render
from django.contrib import messages
from django.db.models import Sum
from .forms import UploadCSVForm
from .utils import load_csv_data, save_fact_ventas
from .models import FactVenta


def inicio(request):
    summary = None
    details = []
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            try:
                processed, summary = load_csv_data(csv_file.file)
                save_fact_ventas(processed)
                details = processed[:100]
                messages.success(request, 'CSV procesado y guardado en la base de datos.')
            except ValueError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, 'Por favor seleccione un archivo CSV válido.')
    else:
        form = UploadCSVForm()

    return render(request, 'ventas/inicio.html', {
        'form': form,
        'summary': summary,
        'details': details,
    })


def tablero(request):
    total = FactVenta.objects.count()
    validos = FactVenta.objects.filter(valido=True).count()
    invalidos = total - validos
    errores = FactVenta.objects.exclude(errores='').count()
    porcentaje_validos = round((validos / total * 100), 2) if total else 0
    porcentaje_invalidos = round((invalidos / total * 100), 2) if total else 0
    ventas_por_categoria = (
        FactVenta.objects
        .values('categoria')
        .annotate(total_monto=Sum('monto'), total_cantidad=Sum('cantidad'))
        .order_by('-total_monto')
    )
    ventas_por_mes = (
        FactVenta.objects
        .exclude(fecha__isnull=True)
        .values('fecha__month')
        .annotate(total_monto=Sum('monto'))
        .order_by('fecha__month')
    )

    return render(request, 'ventas/tablero.html', {
        'total': total,
        'validos': validos,
        'invalidos': invalidos,
        'errores': errores,
        'porcentaje_validos': porcentaje_validos,
        'porcentaje_invalidos': porcentaje_invalidos,
        'ventas_por_categoria': ventas_por_categoria,
        'ventas_por_mes': ventas_por_mes,
    })
