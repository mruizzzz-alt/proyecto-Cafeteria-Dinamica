document.addEventListener('DOMContentLoaded', function () {


  // Función para obtener los JSON de forma segura desde el HTML
  function parseDjangoJson(id, defaultValue) {
        const element = document.getElementById(id);
        if (!element) return defaultValue;
        try {
        return JSON.parse(element.textContent) || defaultValue;
        } catch (e) {
        console.error('Error al leer el elemento ' + id + ':', e);
        return defaultValue;
        }
    }

  // Cargar datos
  const rawMetodos = parseDjangoJson('data-metodos-totales', [0, 0, 0]);
  const tendenciaFechas = parseDjangoJson('data-tendencia-fechas', []);
  const tendenciaTotales = parseDjangoJson('data-tendencia-totales', []);
  const metodosTotales = Array.isArray(rawMetodos) && rawMetodos.length === 3 
    ? rawMetodos.map(v => Number(v) || 0) 
    : [0, 0, 0];

    // 1. Gráfica de Tendencia
    const canvasTendencia = document.getElementById('graficaTendencia');
    if (canvasTendencia) {
        const rawFechas = parseDjangoJson('data-tendencia-fechas', []);
        const rawTotales = parseDjangoJson('data-tendencia-totales', []);

        new Chart(canvasTendencia.getContext('2d'), {
            type: 'line',
            data: {
                labels: rawFechas,
                datasets: [{
                    label: 'Ventas ($)',
                    data: rawTotales,
                    fill: true,
                    backgroundColor: 'rgba(90, 56, 38, 0.15)',
                    borderColor: '#5a3826',
                    borderWidth: 2,
                    tension: 0.3,
                    pointBackgroundColor: '#5a3826',
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '$' + context.raw.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 7,
                            maxRotation: 45,
                            minRotation: 45,
                            align: 'center',
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }
    

    // 2. Gráfica de Métodos de Pago
    const canvasMetodos = document.getElementById('graficaMetodos');

if (canvasMetodos) {

    new Chart(canvasMetodos, {
        type: 'doughnut',
        data: {
            labels: ['Efectivo', 'Tarjeta', 'Transferencia'],
            datasets: [{
                data: [132.10, 13.15, 88],
                backgroundColor: [
                    '#5a3826',
                    '#a0754f',
                    '#d9b48f'
                ]
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

}
});
