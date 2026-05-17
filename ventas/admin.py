from django.contrib import admin
from .models import FactVenta

@admin.register(FactVenta)
class FactVentaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'producto', 'categoria', 'cantidad', 'monto', 'valido', 'fecha')
    list_filter = ('valido', 'categoria', 'fecha')
    search_fields = ('cliente', 'producto', 'tienda', 'ciudad', 'email')
