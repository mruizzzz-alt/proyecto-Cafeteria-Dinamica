const carrito = document.getElementById('carrito');
const elementos1 = document.getElementById('lista-1');   
const lista = document.querySelector('#lista-carrito tbody');
const vaciarCarritoBtn = document.getElementById('vaciar-carrito');
const finalizarCompraBtn = document.getElementById('finalizar-compra');
const totalMonto = document.getElementById('carrito-total-monto');
let articulosCarrito = [];

cargarEventListener();

function cargarEventListener(){
    document.addEventListener('click', clickGlobal);
    vaciarCarritoBtn.addEventListener('click', vaciarCarrito);
    if (finalizarCompraBtn) {
        finalizarCompraBtn.addEventListener('click', finalizarCompra);
    }
    const metodoPagoSelect = document.getElementById('metodo-pago');
    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener('change', function(){
            document.querySelectorAll('.metodo-info').forEach(div => div.style.display = 'none');
            const seleccionado = document.getElementById('info-' + this.value);
            if (seleccionado) seleccionado.style.display = 'block';
        });
    }
    document.addEventListener('DOMContentLoaded', cargarCarritoLS);
}

function mostrarNotificacion(mensaje) {
    const toast = document.getElementById('toast-notificacion');
    if (!toast) return;
    toast.textContent = mensaje;
    toast.style.display = 'block';
    toast.style.opacity = '1';
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s';
        toast.style.opacity = '0';
        setTimeout(() => { toast.style.display = 'none'; toast.style.transition = ''; }, 500);
    }, 2000);
}

function comprarElemento(e){
    e.preventDefault();
    if(e.target.classList.contains('agregar-carrito')){
        const elemento = e.target.parentElement.parentElement;
        leerDatosElemento(elemento);
    }
}

function clickGlobal(e){
    if(e.target.classList.contains('agregar-carrito') || e.target.closest('.agregar-carrito')){
        e.preventDefault();
        const link = e.target.classList.contains('agregar-carrito') ? e.target : e.target.closest('.agregar-carrito');
        const elemento = link.parentElement;
        leerDatosElemento(elemento);
        return;
    }
    if(e.target.classList.contains('borrar')){
        e.preventDefault();
        const id = e.target.getAttribute('data-id');
        eliminarProducto(id);
        return;
    }
    if(e.target.classList.contains('btn-cantidad')){
        e.preventDefault();
        const id = e.target.getAttribute('data-id');
        if(e.target.classList.contains('mas')){
            cambiarCantidad(id, 1);
        } else if(e.target.classList.contains('menos')){
            cambiarCantidad(id, -1);
        }
        return;
    }
}

function leerDatosElemento(elemento){
    let contenedor = elemento;
    if (!contenedor.querySelector('img')) {
        contenedor = elemento.closest('.product') || elemento.closest('.card-product') || elemento.parentElement.parentElement;
    }
    const imgEl = contenedor.querySelector('img');
    const h3El = contenedor.querySelector('h3');
    const precioEl = contenedor.querySelector('.precio');

    const id = elemento.querySelector('a') ? elemento.querySelector('a').getAttribute('data-id') : elemento.getAttribute('data-id');

    if (!imgEl || !h3El || !precioEl) return;

    const existente = articulosCarrito.find(item => item.id === id);
    if(existente){
        existente.cantidad += 1;
    } else {
        const infoElemento = {
            imagen: imgEl.src,
            titulo: h3El.textContent,
            precio: parseFloat(precioEl.textContent.replace('$','')),
            id: id,
            cantidad: 1
        }
        articulosCarrito.push(infoElemento);
    }
    guardarCarritoLS();
    renderCarrito();
    mostrarNotificacion(`🛒 Producto agregado al carrito`);
}

function cambiarCantidad(id, delta){
    const item = articulosCarrito.find(item => item.id === id);
    if(!item) return;
    item.cantidad += delta;
    if(item.cantidad <= 0){
        articulosCarrito = articulosCarrito.filter(i => i.id !== id);
    }
    guardarCarritoLS();
    renderCarrito();
}

function eliminarProducto(id){
    articulosCarrito = articulosCarrito.filter(item => item.id !== id);
    guardarCarritoLS();
    renderCarrito();
}

function renderCarrito(){
    if(!lista) return;
    lista.innerHTML = '';
    let total = 0;
    articulosCarrito.forEach(elemento => {
        total += elemento.precio * elemento.cantidad;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><img src="${elemento.imagen}" width="60" style="border-radius: 10px;"></td>
            <td>
                <div style="font-weight:600;">${elemento.titulo}</div>
                <div style="color:var(--primary-color); font-size:1.3rem;">$${elemento.precio.toFixed(2)}</div>
            </td>
            <td>
                <div class="cantidad-control">
                    <button class="btn-cantidad menos" data-id="${elemento.id}">−</button>
                    <span class="cantidad-numero">${elemento.cantidad}</span>
                    <button class="btn-cantidad mas" data-id="${elemento.id}">+</button>
                </div>
            </td>
            <td><a href="#" class="borrar" data-id="${elemento.id}">×</a></td>
        `;
        lista.appendChild(row);
    });
    if(totalMonto) totalMonto.textContent = '$' + total.toFixed(2);
}

function vaciarCarrito(){
    articulosCarrito = [];
    guardarCarritoLS();
    renderCarrito();
}

function guardarCarritoLS() {
    localStorage.setItem('carrito', JSON.stringify(articulosCarrito));
}

function cargarCarritoLS() {
    articulosCarrito = JSON.parse(localStorage.getItem('carrito')) || [];
    renderCarrito();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function finalizarCompra(e){
    e.preventDefault();
    if (articulosCarrito.length === 0) {
        mostrarNotificacion('Tu carrito está vacío');
        return;
    }

    const metodoPagoSelect = document.getElementById('metodo-pago');
    const metodoPago = metodoPagoSelect ? metodoPagoSelect.value : 'efectivo';

    if (metodoPago === 'tarjeta') {
        const numTarjeta = document.getElementById('numero-tarjeta').value.trim().replace(/\s/g, '');
        const fecha = document.getElementById('fecha-tarjeta').value.trim();
        const cvv = document.getElementById('cvv-tarjeta').value.trim();
        if (numTarjeta.length < 13 || !/^\d+$/.test(numTarjeta)) {
            mostrarNotificacion('Ingresa un número de tarjeta válido');
            return;
        }
        if (!/^\d{2}\/\d{2}$/.test(fecha)) {
            mostrarNotificacion('Ingresa la fecha en formato MM/AA');
            return;
        }
        if (cvv.length !== 3 || !/^\d+$/.test(cvv)) {
            mostrarNotificacion('Ingresa un CVV válido de 3 dígitos');
            return;
        }
    }

    const items = [];
    articulosCarrito.forEach(item => {
        for(let i = 0; i < item.cantidad; i++){
            items.push({ id: item.id });
        }
    });

    finalizarCompraBtn.textContent = 'Procesando...';

    fetch('/finalizar-compra/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ items: items, metodo_pago: metodoPago }),
    })
    .then(response => response.json())
    .then(data => {
        finalizarCompraBtn.textContent = 'Finalizar compra';
        if (data.ok) {
            vaciarCarrito();
            mostrarNotificacion('✅ ¡Pedido #' + data.pedido_id + ' confirmado! Te contactaremos pronto.');
        } else {
            mostrarNotificacion('Error: ' + (data.error || 'no se pudo procesar la compra'));
        }
    })
    .catch(() => {
        finalizarCompraBtn.textContent = 'Finalizar compra';
        mostrarNotificacion('Error de conexión, intenta de nuevo');
    });
}