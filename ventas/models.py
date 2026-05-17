from django.db import models


class FactVenta(models.Model):
    cliente = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, blank=True)
    region = models.CharField(max_length=100, blank=True)
    producto = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100, blank=True)
    tienda = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    tipo_tienda = models.CharField(max_length=100, blank=True)
    fecha = models.DateField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valido = models.BooleanField(default=True)
    errores = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente} - {self.producto} - {self.monto}"
