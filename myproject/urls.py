# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView # Importar esta clase para la redirección

urlpatterns = [
    # Redirige la URL raíz (vacía) a la vista del dashboard del primer empleado
    # Esto resolverá el 404 en http://0.0.0.0:8000/
    path('', RedirectView.as_view(url='/primerempleado/', permanent=False)),

    path('admin/', admin.site.urls),
    # Incluye las URLs de tu aplicación gestion_impresion.
    # Como gestion_impresion/urls.py ya tiene 'primerempleado/' y 'segundoempleado/',
    # al incluirlo con path('', include(...)), se accede directamente a /primerempleado/ y /segundoempleado/
    path('', include('gestion_impresion.urls')),
]

# Sirve los archivos de medios (subidos por usuarios) durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
