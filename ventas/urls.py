from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('panel/', views.tablero, name='panel'),
    path('tablero/', views.tablero, name='tablero'),
]
