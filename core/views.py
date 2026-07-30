from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Producto, Pedido, ItemPedido, Blog, Categoria
from .forms import RegistroForm
import json
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            messages.success(request, 'Cuenta creada correctamente. Ya podés iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def finalizar_compra(request):

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)

    if not items:
        return JsonResponse({'ok': False, 'error': 'El carrito está vacío'}, status=400)

    metodos_validos = ['efectivo', 'tarjeta', 'transferencia']
    if metodo_pago not in metodos_validos:
        metodo_pago = 'efectivo'

    conteo = {}
    for item in items:
        pid = item.get('id')
        conteo[pid] = conteo.get(pid, 0) + 1

    productos_map = {}
    for pid in conteo:
        try:
            productos_map[pid] = Producto.objects.get(pk=pid)
        except (Producto.DoesNotExist, ValueError):
            return JsonResponse({'ok': False, 'error': f'Producto {pid} no encontrado'}, status=400)

    for pid, cantidad in conteo.items():
        if productos_map[pid].stock < cantidad:
            return JsonResponse({'ok': False, 'error': f'Stock insuficiente para {productos_map[pid].nombre}'}, status=400)

    pedido = Pedido.objects.create(usuario=request.user, metodo_pago=metodo_pago)

    items_factura = []
    for pid, cantidad in conteo.items():
        producto = productos_map[pid]
        ItemPedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
        )
        producto.stock -= cantidad
        producto.save()
        items_factura.append({
            'nombre': producto.nombre,
            'cantidad': cantidad,
            'precio_unitario': float(producto.precio),
            'subtotal': float(producto.precio) * cantidad,
        })

    fecha_local = timezone.localtime(pedido.fecha)

    return JsonResponse({
        'ok': True,
        'pedido_id': pedido.id,
        'codigo': pedido.codigo,
        'fecha': fecha_local.strftime('%d/%m/%Y'),
        'hora': fecha_local.strftime('%H:%M'),
        'estado': pedido.get_estado_display(),
        'metodo_pago': pedido.get_metodo_pago_display(),
        'cliente': request.user.first_name or request.user.username,
        'items': items_factura,
        'total': float(pedido.total()),
    })

@login_required
def mi_cuenta(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    profile, _ = Profile.objects.get_or_create(user=request.user)
    pedidos = request.user.pedido_set.order_by('-fecha')[:10]

    if request.method == 'POST':
        if 'guardar_perfil' in request.POST:
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.save()
            profile.phone = request.POST.get('phone', profile.phone)
            if request.FILES.get('photo'):
                profile.photo = request.FILES['photo']
            profile.save()
            messages.success(request, 'Cuenta actualizada correctamente.')
            return redirect('mi_cuenta')

        if 'cambiar_password' in request.POST:
            form_password = PasswordChangeForm(request.user, request.POST)
            if form_password.is_valid():
                user = form_password.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('mi_cuenta')
        else:
            form_password = PasswordChangeForm(request.user)
    else:
        form_password = PasswordChangeForm(request.user)

    return render(request, 'tienda/mi_cuenta.html', {
        'profile': profile,
        'pedidos': pedidos,
        'form_password': form_password,
    })

@login_required
def perfil(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.save()
        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('perfil')
    return render(request, 'registration/perfil.html', {'profile': profile})

@staff_member_required
def lista_blogs(request):
    blogs = Blog.objects.all().order_by('-fecha')
    return render(request, 'blogs/lista.html', {'blogs': blogs})

@staff_member_required
def agregar_blog(request):
    if request.method == 'POST':
        Blog.objects.create(
            titulo=request.POST.get('titulo'),
            resumen=request.POST.get('resumen'),
            contenido=request.POST.get('contenido', ''),
            imagen=request.FILES.get('imagen'),
        )
        messages.success(request, 'Blog agregado correctamente.')
        return redirect('lista_blogs')
    return render(request, 'blogs/form.html', {'accion': 'Agregar'})

@staff_member_required
def editar_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.titulo = request.POST.get('titulo')
        blog.resumen = request.POST.get('resumen')
        blog.contenido = request.POST.get('contenido', '')
        if request.FILES.get('imagen'):
            blog.imagen = request.FILES['imagen']
        blog.save()
        messages.success(request, 'Blog actualizado correctamente.')
        return redirect('lista_blogs')
    return render(request, 'blogs/form.html', {'accion': 'Editar', 'blog': blog})

@staff_member_required
def eliminar_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog eliminado correctamente.')
        return redirect('lista_blogs')
    return render(request, 'blogs/confirmar_eliminar.html', {'blog': blog})

@staff_member_required
def lista_categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'categorias/lista.html', {'categorias': categorias})

@staff_member_required
def agregar_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre, imagen=request.FILES.get('imagen'))
            messages.success(request, 'Categoría agregada correctamente.')
        return redirect('lista_categorias')
    return render(request, 'categorias/form.html', {'accion': 'Agregar'})

@staff_member_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre', categoria.nombre).strip()
        if request.FILES.get('imagen'):
            categoria.imagen = request.FILES['imagen']
        categoria.save()
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('lista_categorias')
    return render(request, 'categorias/form.html', {'accion': 'Editar', 'categoria': categoria})

@staff_member_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('lista_categorias')
    return render(request, 'categorias/confirmar_eliminar.html', {'categoria': categoria})

@staff_member_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('categoria__nombre', 'nombre')
    return render(request, 'productos/lista.html', {'productos': productos})

@staff_member_required
def agregar_producto(request):
    if request.method == 'POST':
        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            categoria_id=request.POST.get('categoria'),
            precio=request.POST.get('precio'),
            stock=request.POST.get('stock'),
            foto=request.FILES.get('foto')
        )
        messages.success(request, 'Producto agregado correctamente.')
        return redirect('lista_productos')
    return render(request, 'productos/form.html', {'accion': 'Agregar', 'categorias': Categoria.objects.all()})

@staff_member_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.categoria_id = request.POST.get('categoria')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        if request.FILES.get('foto'):
            producto.foto = request.FILES['foto']
        producto.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('lista_productos')
    return render(request, 'productos/form.html', {'accion': 'Editar', 'producto': producto, 'categorias': Categoria.objects.all()})

@staff_member_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, 'Producto eliminado.')
    return redirect('lista_productos')



@staff_member_required
def lista_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad', 1))
        producto = get_object_or_404(Producto, pk=producto_id)

        if cantidad > producto.stock:
            messages.error(request, f'No hay suficiente stock de {producto.nombre}.')
        else:
            pedido = Pedido.objects.create(usuario=request.user)
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            producto.stock -= cantidad
            producto.save()
            messages.success(request, f'Pedido #{pedido.id} creado correctamente.')
        return redirect('lista_pedidos')

    return render(request, 'pedidos/lista.html', {'pedidos': pedidos, 'productos': productos})

def blog_detalle(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'tienda/blog_detalle.html', {'blog': blog})

def tienda_index(request):
    q = request.GET.get('q', '').strip()
    productos_destacados = Producto.objects.order_by('-creado')[:4]
    productos_especiales = Producto.objects.filter(categoria__nombre='Café')[:4]
    if q:
        productos_destacados = Producto.objects.filter(nombre__icontains=q)
        productos_especiales = Producto.objects.none()

    context = {
        'productos_destacados': productos_destacados,
        'productos_especiales': productos_especiales,
        'blogs': Blog.objects.order_by('-fecha')[:3],
        'categorias': Categoria.objects.all(),
        'query': q,
    }
    return render(request, 'tienda/index.html', context)
def tienda_cafe(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(categoria__nombre='Café')
    if q:
        productos = productos.filter(nombre__icontains=q)
    context = {'productos': productos, 'query': q}
    return render(request, 'tienda/cafe.html', context)


def tienda_desayuno(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(categoria__nombre='Desayuno')
    if q:
        productos = productos.filter(nombre__icontains=q)
    context = {'productos': productos, 'query': q}
    return render(request, 'tienda/desayuno.html', context)


def tienda_postre(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(categoria__nombre='Postre')
    if q:
        productos = productos.filter(nombre__icontains=q)
    context = {'productos': productos, 'query': q}
    return render(request, 'tienda/postre.html', context)


def tienda_categoria(request, nombre):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(categoria__nombre=nombre)
    if q:
        productos = productos.filter(nombre__icontains=q)
    context = {'productos': productos, 'query': q, 'categoria_nombre': nombre}
    return render(request, 'tienda/categoria.html', context)
