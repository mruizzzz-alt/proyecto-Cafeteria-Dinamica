from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.models import Profile, Producto, Pedido
import json
from datetime import date,datetime, timedelta

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        return redirect('tienda_index')

    profile, created = Profile.objects.get_or_create(user=request.user)

    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    stock_bajo = Producto.objects.filter(stock__lt=5).count()
    valor_inventario = sum(p.precio * p.stock for p in Producto.objects.all())
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M")

    ultimos_pedidos_qs = Pedido.objects.select_related('usuario').order_by('-fecha')[:5]
    ultimos_pedidos = [
        {
            'id': p.id,
            'cliente': p.usuario.first_name or p.usuario.username,
            'total': p.total(),
            'estado': p.get_estado_display(),
        }
        for p in ultimos_pedidos_qs
    ]

    from django.contrib.auth.models import User
    clientes_recientes_qs = (
        User.objects.filter(pedido__isnull=False)
        .distinct()
        .order_by('-date_joined')[:5]
    )
    clientes_recientes = [
        {'nombre': u.first_name or u.username, 'email': u.email}
        for u in clientes_recientes_qs
    ]

    from core.models import Categoria
    categorias = [
        {'nombre': c.nombre, 'total': c.producto_set.count()}
        for c in Categoria.objects.all()
    ]

    productos_stock_bajo = Producto.objects.filter(stock__lt=5).order_by('stock')

    return render(request, "index.html", {
        "profile": profile,
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "stock_bajo": stock_bajo,
        "valor_inventario": valor_inventario,
        "fecha": fecha,
        "hora": hora,
        "ultimos_pedidos": ultimos_pedidos,
        "clientes_recientes": clientes_recientes,
        "categorias": categorias,
        "productos_stock_bajo": productos_stock_bajo,
    })

@login_required
def redireccion_login(request):
    if request.user.is_staff:
        return redirect('index')          # Dashboard AdminLTE
    else:
        return redirect('tienda_index')   # Página principal de la cafetería

def index2(request):
    base_qs = Pedido.objects.prefetch_related('items__producto').select_related('usuario')
    context = {
        'pedidos_nuevos': base_qs.filter(estado='nuevo').order_by('-fecha'),
        'pedidos_preparacion': base_qs.filter(estado='preparacion').order_by('-fecha'),
        'pedidos_listos': base_qs.filter(estado='listo').order_by('-fecha'),
        'pedidos_entregados': base_qs.filter(estado='entregado').order_by('-fecha'),
        'pedidos_historial': base_qs.all().order_by('-fecha'),
    }
    return render(request, "pedidos.html", context)

def cambiar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado = request.POST.get('estado')
        estados_validos = ['nuevo', 'preparacion', 'listo', 'entregado']
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
    return redirect('pedidos')

def index3(request):
    from django.contrib.auth.models import User
    clientes_qs = User.objects.filter(pedido__isnull=False).distinct().select_related('profile').prefetch_related('pedido_set__items__producto')
    clientes = []
    for user in clientes_qs:
        pedidos = user.pedido_set.all()
        clientes.append({
            'user': user,
            'total_pedidos': pedidos.count(),
            'total_gastado': sum(p.total() for p in pedidos),
            'ultimo_pedido': max((p.fecha for p in pedidos), default=None),
            'pedidos': pedidos.order_by('-fecha'),
        })
    clientes.sort(key=lambda c: c['total_gastado'], reverse=True)
    return render(request, "index3.html", {'clientes': clientes})

def ventas(request):
    hoy = date.today()
    pedidos = list(Pedido.objects.prefetch_related('items'))

    # Helper para obtener la fecha sin hora de un pedido
    def get_fecha(p):
        return p.fecha.date()

    ventas_hoy = sum(p.total() for p in pedidos if get_fecha(p) == hoy)
    total_pedidos_hoy = sum(1 for p in pedidos if get_fecha(p) == hoy)
    primer_dia_mes = hoy.replace(day=1)
    ventas_mes = sum(p.total() for p in pedidos if get_fecha(p) >= primer_dia_mes)

    # Gráfica 1: Tendencia 14 días
    # Gráfica 1: Tendencia últimos 14 días
    dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]  # últimos 7 días

    tendencia_fechas = [
        d.strftime('%d/%m') 
        for d in dias
    ]

    tendencia_totales = [
        float(sum(p.total() for p in pedidos if get_fecha(p) == d))
        for d in dias
    ]

    # Gráfica 2: Métodos de pago (Normalizado a minúsculas con .lower())
    metodos_totales = {'efectivo': 0.0, 'tarjeta': 0.0, 'transferencia': 0.0}
    for p in pedidos:
        metodo = str(p.metodo_pago).lower().strip() if p.metodo_pago else ''
        if metodo in metodos_totales:
            metodos_totales[metodo] += float(p.total())

    reportes = sorted(pedidos, key=lambda p: p.fecha, reverse=True)[:20]
    print("JSON DONA:", json.dumps([
        float(metodos_totales['efectivo']),
        float(metodos_totales['tarjeta']),
        float(metodos_totales['transferencia'])
    ]))
    context = {
        'ventas_hoy': ventas_hoy,
        'ventas_mes': ventas_mes,
        'total_pedidos_hoy': total_pedidos_hoy,
        'tendencia_fechas_json': json.dumps(tendencia_fechas),
        'tendencia_totales_json': json.dumps(tendencia_totales),
        'metodos_totales_json': json.dumps([
            float(metodos_totales['efectivo']), 
            float(metodos_totales['tarjeta']), 
            float(metodos_totales['transferencia'])
        ]),
        'metodo_efectivo': metodos_totales['efectivo'],
        'metodo_tarjeta': metodos_totales['tarjeta'],
        'metodo_transferencia': metodos_totales['transferencia'],
        'reportes': reportes,
    }
    return render(request, 'ventas.html', context)

def configuracion(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    from core.models import Negocio, Profile

    # 1. Aseguramos que siempre exista al menos UN registro de Negocio
    negocio, _ = Negocio.objects.get_or_create(id=1)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'guardar_negocio' in request.POST or 'logo' in request.FILES:
            negocio.nombre = request.POST.get('nombre', '')
            negocio.direccion = request.POST.get('direccion', '')
            negocio.horario = request.POST.get('horario', '')
            negocio.telefono = request.POST.get('telefono', '')
            negocio.email = request.POST.get('email', '')
            
            # Guardar redes sociales
            negocio.facebook = request.POST.get('facebook', '')
            negocio.youtube = request.POST.get('youtube', '')
            negocio.tiktok = request.POST.get('tiktok', '')
            negocio.pinterest = request.POST.get('pinterest', '')
            negocio.instagram = request.POST.get('instagram', '')
            
            if request.FILES.get('logo'):
                negocio.logo = request.FILES['logo']
                
            negocio.save()
            return redirect('configuracion')

        if 'guardar_perfil' in request.POST:
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.save()
            profile.phone = request.POST.get('phone', profile.phone)
            profile.bio = request.POST.get('bio', profile.bio)
            if request.FILES.get('photo'):
                profile.photo = request.FILES['photo']
            profile.save()
            return redirect('configuracion')

        if 'cambiar_password' in request.POST:
            form_password = PasswordChangeForm(request.user, request.POST)
            if form_password.is_valid():
                user = form_password.save()
                update_session_auth_hash(request, user)
                return redirect('configuracion')
        else:
            form_password = PasswordChangeForm(request.user)
    else:
        form_password = PasswordChangeForm(request.user)

    context = {
        'negocio': negocio,
        'profile': profile,
        'form_password': form_password,
    }
    return render(request, 'configuracion.html', context)

def tienda_categoria(request, nombre):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(categoria__nombre=nombre)
    if q:
        productos = productos.filter(nombre__icontains=q)
    context = {
        'productos': productos,
        'query': q,
        'categoria_nombre': nombre,
    }
    return render(request, 'tienda/categoria.html', context)