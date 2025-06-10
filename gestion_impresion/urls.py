from django.urls import path
from . import views

app_name = 'gestion_impresion'
urlpatterns = [
    path('primerempleado/', views.primer_empleado_dashboard_view, name='primer_empleado_dashboard'),
    path('segundoempleado/', views.segundo_empleado_dashboard_view, name='segundo_empleado_dashboard'),
]
