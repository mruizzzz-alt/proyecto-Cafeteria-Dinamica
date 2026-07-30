from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string


def generar_codigo_pedido():
    caracteres = string.ascii_uppercase + string.digits
    return 'CAF-' + ''.join(random.choices(caracteres, k=6))

class Negocio(models.Model):
    nombre = models.CharField(max_length=100, default='Café Hallyu')
    logo = models.ImageField(upload_to='negocio/', blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True)
    horario = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return self.user.username


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    foto = models.ImageField(upload_to='productos/', blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Blog(models.Model):
    titulo = models.CharField(max_length=150)
    imagen = models.ImageField(upload_to='blogs/', blank=True, null=True)
    resumen = models.TextField(max_length=500)
    contenido = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    ESTADOS = [
        ('nuevo', 'Nuevo'),
        ('preparacion', 'En preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='nuevo')

    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)

    codigo = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
        default=generar_codigo_pedido,
        help_text="Código que el cliente presenta al repartidor/atención para verificar el pedido."
    )

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario