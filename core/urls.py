from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='tienda_index'), name='logout'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('registro/', views.registro, name='registro'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('blogs/', views.lista_blogs, name='lista_blogs'),
    path('blogs/agregar/', views.agregar_blog, name='agregar_blog'),
    path('blogs/editar/<int:pk>/', views.editar_blog, name='editar_blog'),
    path('blogs/eliminar/<int:pk>/', views.eliminar_blog, name='eliminar_blog'),
    path('categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('', views.tienda_index, name='tienda_index'),
    path('blog/<int:pk>/', views.blog_detalle, name='blog_detalle'),
    path('tienda/cafe/', views.tienda_cafe, name='tienda_cafe'),
    path('tienda/desayuno/', views.tienda_desayuno, name='tienda_desayuno'),
    path('tienda/postre/', views.tienda_postre, name='tienda_postre'),
    path('categoria/<path:nombre>/', views.tienda_categoria, name='tienda_categoria'),
]
