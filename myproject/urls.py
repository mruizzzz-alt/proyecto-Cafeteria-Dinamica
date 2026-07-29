"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('panel/', views.index, name='index'),
    path('inicio/', views.redireccion_login, name='redireccion_login'),
    path('admin/', admin.site.urls),
    path('pedidos/', views.index2, name='pedidos'),
    path('pedidos/<int:pedido_id>/estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('index3/', views.index3, name='index3'),
    path('ventas/', views.ventas, name='ventas'),
    path('configuracion/', views.configuracion, name='configuracion'),

    # Autenticación (login, logout, cambio de contraseña)
    path('accounts/', include('django.contrib.auth.urls')),

    # Perfil y registro (los vamos a crear en core)
    path('', include('core.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
