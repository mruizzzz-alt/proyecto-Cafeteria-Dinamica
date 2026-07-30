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

/* ==========================================
   MODAL DE CÓDIGO DE VERIFICACIÓN DEL PEDIDO
   ========================================== */

function inyectarEstilosModalCodigo() {
    if (document.getElementById('estilos-modal-codigo')) return;
    const style = document.createElement('style');
    style.id = 'estilos-modal-codigo';
    style.textContent = `
        .modal-codigo-overlay {
            position: fixed;
            inset: 0;
            background: rgba(43, 33, 24, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 20px;
            overflow-y: auto;
        }
        .ticket-caja {
            background: #FDFBF7;
            border-radius: 10px;
            max-width: 340px;
            width: 100%;
            padding: 24px 22px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            font-family: 'Courier New', monospace;
            color: #2B2118;
            max-height: 90vh;
            overflow-y: auto;
            font-size: 0.85rem;
            line-height: 1.5;
        }
        .ticket-linea {
            border: none;
            border-top: 1px dashed #5A3826;
            margin: 10px 0;
        }
        .ticket-negocio {
            text-align: center;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--primary-color, #5A3826);
            font-size: 0.95rem;
        }
        .ticket-pedido {
            text-align: center;
            margin: 10px 0;
        }
        .ticket-label {
            color: #8a7566;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .ticket-codigo-label {
            text-align: center;
            color: #8a7566;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-top: 6px;
        }
        .ticket-codigo-valor {
            text-align: center;
            font-weight: 700;
            font-size: 1.3rem;
            letter-spacing: 0.1em;
            color: var(--primary-color, #5A3826);
            margin: 4px 0 6px;
        }
        .ticket-bloque {
            margin: 10px 0;
        }
        .ticket-titulo-seccion {
            font-weight: 700;
            margin-bottom: 4px;
        }
        .ticket-item {
            display: flex;
            justify-content: space-between;
            gap: 8px;
        }
        .ticket-total-fila {
            display: flex;
            justify-content: space-between;
            font-weight: 700;
            font-size: 1.05rem;
            margin: 4px 0;
        }
        .ticket-pie {
            text-align: center;
            font-size: 0.78rem;
            margin-top: 4px;
        }
        .ticket-pie-codigo {
            text-align: center;
            font-weight: 700;
            letter-spacing: 0.1em;
            font-size: 1rem;
            margin: 8px 0 4px;
            color: var(--primary-color, #5A3826);
        }
        .ticket-cerrar {
            display: block;
            width: 100%;
            background: var(--primary-color, #5A3826);
            color: #fff;
            border: none;
            border-radius: 20px;
            padding: 11px 0;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            font-family: inherit;
            margin-top: 14px;
        }
        .ticket-cerrar:hover {
            opacity: 0.9;
        }
    `;
    document.head.appendChild(style);
}

function mostrarCodigoPedido(data) {
    inyectarEstilosModalCodigo();

    const existente = document.getElementById('modal-codigo-overlay');
    if (existente) existente.remove();

    const filas = (data.items || []).map(item => {
        const izquierda = `${item.cantidad} x ${item.nombre}`;
        return `<div class="ticket-item"><span>${izquierda}</span><span>$${item.subtotal.toFixed(2)}</span></div>`;
    }).join('');

    const overlay = document.createElement('div');
    overlay.className = 'modal-codigo-overlay';
    overlay.id = 'modal-codigo-overlay';
    overlay.innerHTML = `
        <div class="ticket-caja">
            <div class="ticket-negocio">CAFÉ HALLYU LETTERS</div>
            <hr class="ticket-linea">

            <div class="ticket-pedido">Pedido #${data.pedido_id}</div>

            <div class="ticket-codigo-label">Código de retiro</div>
            <div class="ticket-codigo-valor">${data.codigo}</div>

            <hr class="ticket-linea">

            <div class="ticket-bloque">
                <div class="ticket-label">Cliente</div>
                <div>${data.cliente}</div>
            </div>
            <div class="ticket-bloque">
                <div class="ticket-label">Fecha</div>
                <div>${data.fecha} &nbsp; ${data.hora}</div>
            </div>

            <hr class="ticket-linea">

            <div class="ticket-titulo-seccion">Productos</div>
            ${filas}

            <hr class="ticket-linea">

            <div class="ticket-total-fila"><span>TOTAL</span><span>$${data.total.toFixed(2)}</span></div>

            <hr class="ticket-linea">

            <div class="ticket-bloque">
                <div class="ticket-label">Método de pago</div>
                <div>${data.metodo_pago}</div>
            </div>
            <div class="ticket-bloque">
                <div class="ticket-label">Estado</div>
                <div>${data.estado}</div>
            </div>

            <hr class="ticket-linea">

            <div class="ticket-pie">Presente este código al retirar<br>su pedido.</div>
            <div class="ticket-pie-codigo">${data.codigo}</div>

            <button type="button" class="ticket-cerrar" id="cerrar-modal-codigo">Entendido</button>
        </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('cerrar-modal-codigo').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.remove();
    });
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
            mostrarCodigoPedido(data);
        } else {
            mostrarNotificacion('Error: ' + (data.error || 'no se pudo procesar la compra'));
        }
    })
    .catch(() => {
        finalizarCompraBtn.textContent = 'Finalizar compra';
        mostrarNotificacion('Error de conexión, intenta de nuevo');
    });
}