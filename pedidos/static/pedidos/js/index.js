/* =========================================
   1. INICIALIZACIÓN GLOBAL (Se ejecuta al cargar)
   ========================================= */
document.addEventListener('DOMContentLoaded', function() {
    // A. Gestión del Modo Oscuro
    initThemeToggle();

    // B. Inicializar Plugins
    initPlugins();

    // C. Formulario Pedidos
    if (document.getElementById('pedidoForm')) {
        initPedidoForm();
    }

    // D. Ordenamiento Tablas
    if (document.querySelector('th.sortable')) {
        initTableSorting();
    }

    // E. Gráficos del Dashboard (NUEVO)
    if (document.getElementById('chartEstados')) {
        initDashboardCharts();
    }
});


/* =========================================
   2. FUNCIONES DE TEMA (MODO OSCURO)
   ========================================= */
function initThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    const isDark = localStorage.getItem('color-theme') === 'dark' ||
                   (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);

    if (isDark) {
        htmlElement.classList.add('dark');
    } else {
        htmlElement.classList.remove('dark');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            if (htmlElement.classList.contains('dark')) {
                htmlElement.classList.remove('dark');
                localStorage.setItem('color-theme', 'light');
            } else {
                htmlElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
            }
            if ($('#id_detalles_pedido').length) {
                $('#id_detalles_pedido').summernote('destroy');
                initPlugins();
            }
        });
    }
}

/* =========================================
   3. CONFIGURACIÓN DE PLUGINS (JQUERY)
   ========================================= */
function initPlugins() {
    // A. Configuración Select2
    if ($('.select2').length) {
        $('.select2').select2({
            width: '100%',
            placeholder: "Seleccione una opción...",
            allowClear: true
        });
    }

    // B. Configuración Summernote (Editor de Texto)
    if ($('#id_detalles_pedido').length) {
        let isDark = document.documentElement.classList.contains('dark');

        $('#id_detalles_pedido').summernote({
            placeholder: 'Escribe aquí las especificaciones (Solo texto, no imágenes)...',
            tabsize: 2,
            height: 200,
            disableDragAndDrop: true,
            toolbar: [
                ['style', ['bold', 'italic', 'clear']],
                ['para', ['ul', 'ol']]
            ],
            callbacks: {
                onInit: function() {
                    if(isDark) {
                        $('.note-editable').css({'background-color': '#262626', 'color': 'white'});
                        $('.note-editor').css({'border-color': '#404040'});
                    }
                },
                // CANDADO 1: Bloqueo de subida directa (Botón o Drag & Drop)
                onImageUpload: function(files) {
                    alert('⚠️ NO ESTÁ PERMITIDO pegar imágenes aquí.\n\nPor favor, usa el campo "Imagen de Referencia".');
                },
                // CANDADO 2: Bloqueo de Pegado (Ctrl+V)
                onPaste: function (e) {
                    // 1. Detenemos la acción estándar inmediatamente
                    e.preventDefault();

                    var bufferText = '';

                    // 2. Intentamos recuperar el contenido como TEXTO PLANO
                    if (e.originalEvent && e.originalEvent.clipboardData) {
                        bufferText = e.originalEvent.clipboardData.getData('text/plain');
                    } else if (window.clipboardData) {
                        bufferText = window.clipboardData.getData('Text');
                    }

                    // 3. Verificamos si hay texto real
                    if (bufferText && bufferText.trim().length > 0) {
                        // Solución al Warning: Usamos la API nativa de Summernote en vez de execCommand
                        $('#id_detalles_pedido').summernote('insertText', bufferText);
                    } else {
                        // Si no hay texto (es una imagen pura), mostramos la alerta
                        alert('NO ESTÁ PERMITIDO pegar imágenes aquí.\n\nPor favor, usa el campo "Imagen de Referencia".');
                    }
                }
            }
        });
    }
}

/* =========================================
   4. LÓGICA DEL FORMULARIO PEDIDOS (AJAX)
   ========================================= */
function initPedidoForm() {
    const $selectCliente = $('#id_cliente');
    const sectionDetalles = document.getElementById('section-detalles-pedido');
    const sectionBuscar = document.getElementById('section-buscar-cliente');
    const sectionCrear = document.getElementById('section-crear-cliente');
    const btnToggleCrear = document.getElementById('btn-toggle-crear');
    const btnCancelarCrear = document.getElementById('btn-cancelar-crear');
    const btnGuardarApi = document.getElementById('btn-guardar-cliente-api');

    function checkClienteSeleccionado() {
        if ($selectCliente.val()) {
            sectionDetalles.classList.remove('hidden', 'opacity-50');
            sectionDetalles.classList.add('opacity-100');
        } else {
            sectionDetalles.classList.add('hidden', 'opacity-50');
            sectionDetalles.classList.remove('opacity-100');
        }
    }
    $selectCliente.on('change', checkClienteSeleccionado);
    checkClienteSeleccionado();

    if(btnToggleCrear) {
        btnToggleCrear.addEventListener('click', () => {
            sectionBuscar.classList.add('hidden');
            sectionCrear.classList.remove('hidden');
        });
    }

    if(btnCancelarCrear) {
        btnCancelarCrear.addEventListener('click', () => {
            sectionCrear.classList.add('hidden');
            sectionBuscar.classList.remove('hidden');
            document.getElementById('cliente-api-error').classList.add('hidden');
        });
    }

    if (btnGuardarApi) {
        btnGuardarApi.addEventListener('click', function() {
            const nombre = document.getElementById('new_client_nombre').value;
            const telefono = document.getElementById('new_client_telefono').value;
            const email = document.getElementById('new_client_email').value;

            if(!nombre || !telefono) {
                const errorDiv = document.getElementById('cliente-api-error');
                errorDiv.innerText = 'Nombre y Teléfono son obligatorios';
                errorDiv.classList.remove('hidden');
                return;
            }

            const originalText = btnGuardarApi.innerHTML;
            btnGuardarApi.disabled = true;
            btnGuardarApi.innerHTML = '<span class="material-icons-round animate-spin text-sm mr-2">refresh</span> Guardando...';

            const apiUrl = btnGuardarApi.getAttribute('data-url');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams({ 'nombre': nombre, 'telefono': telefono, 'email': email })
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    const newOption = new Option(data.nombre, data.id, true, true);
                    $selectCliente.append(newOption).trigger('change');
                    sectionCrear.classList.add('hidden');
                    sectionBuscar.classList.remove('hidden');
                    document.getElementById('new_client_nombre').value = '';
                    document.getElementById('new_client_telefono').value = '';
                    document.getElementById('new_client_email').value = '';
                    checkClienteSeleccionado();
                } else {
                    const errorDiv = document.getElementById('cliente-api-error');
                    errorDiv.innerText = 'Error: ' + JSON.stringify(data.errors);
                    errorDiv.classList.remove('hidden');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('cliente-api-error').innerText = 'Error de conexión';
                document.getElementById('cliente-api-error').classList.remove('hidden');
            })
            .finally(() => {
                btnGuardarApi.disabled = false;
                btnGuardarApi.innerHTML = originalText;
            });
        });
    }
}

/* =========================================
   5. ORDENAMIENTO DE TABLAS (NUEVO)
   ========================================= */
function initTableSorting() {
    // Buscamos todas las cabeceras que tengan la clase .sortable
    const headers = document.querySelectorAll('th.sortable');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            // 1. Obtener el campo por el cual ordenar (ej: 'cliente__nombre')
            const sortField = header.getAttribute('data-sort');

            // 2. Leer la URL actual para ver qué filtros ya existen
            const currentUrl = new URL(window.location.href);
            const currentSort = currentUrl.searchParams.get('orden');

            // 3. Calcular el nuevo orden
            let newSort = sortField;

            // Si ya estamos ordenando por este campo, lo invertimos (agregamos el guion -)
            if (currentSort === sortField) {
                newSort = '-' + sortField;
            }
            // (Si ya estaba invertido, al asignar newSort = sortField volvemos al orden normal)

            // 4. Actualizar el parámetro en la URL
            currentUrl.searchParams.set('orden', newSort);

            // 5. Recargar la página con la nueva URL
            // (Esto preserva automáticamente la búsqueda y otros filtros que ya estén en la URL)
            window.location.href = currentUrl.toString();
        });
    });
}

/* =========================================
   6. GRÁFICOS DEL DASHBOARD (CHART.JS)
   ========================================= */
function initDashboardCharts() {
    // 1. Recuperar los datos desde los script tags generados por Django
    const estadosLabels = JSON.parse(document.getElementById('data-estados-labels').textContent);
    const estadosData = JSON.parse(document.getElementById('data-estados-data').textContent);
    const clientesLabels = JSON.parse(document.getElementById('data-clientes-labels').textContent);
    const clientesData = JSON.parse(document.getElementById('data-clientes-data').textContent);

    // 2. Definición de Colores
    const colorPendiente = '#EF4444'; // Rojo
    const colorProceso = '#EAB308';   // Amarillo
    const colorTerminado = '#22C55E'; // Verde
    const coloresClientes = [
        '#FACC15', '#A16207', '#CA8A04', '#EAB308', '#FEF08A' // Gama Dorada
    ];

    // 3. Configuración de Tema y Colores de Fuente
    const isDark = document.documentElement.classList.contains('dark');

    // CORRECCIÓN 2: Color más oscuro para modo claro (casi negro) para mejor lectura
    const textColor = isDark ? '#cbd5e1' : '#111827';
    const gridColor = isDark ? '#404040' : '#e2e8f0';

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: textColor,
                    font: { family: "'Inter', sans-serif", size: 12 }
                }
            }
        },
        layout: { padding: 10 }
    };

    // 4. GRÁFICO 1: ESTADOS
    const ctxEstados = document.getElementById('chartEstados').getContext('2d');
    new Chart(ctxEstados, {
        type: 'doughnut',
        data: {
            labels: estadosLabels,
            datasets: [{
                data: estadosData,
                backgroundColor: [colorPendiente, colorProceso, colorTerminado],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: commonOptions
    });

    // 5. GRÁFICO 2: TOP CLIENTES (MODO BARRAS HORIZONTALES)
    const ctxClientes = document.getElementById('chartClientes').getContext('2d');
    new Chart(ctxClientes, {
        type: 'bar',
        data: {
            labels: clientesLabels,
            datasets: [{
                label: 'Cantidad de Pedidos',
                data: clientesData,
                backgroundColor: coloresClientes,
                borderRadius: 4,
                barThickness: 20,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.raw + ' Pedidos';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        stepSize: 1,
                        color: textColor // Color oscuro corregido
                    },
                    // CORRECCIÓN 3: Etiqueta explicativa en el eje X
                    title: {
                        display: true,
                        text: 'Total de Pedidos Realizados',
                        color: isDark ? '#9ca3af' : '#6b7280',
                        font: {
                            size: 11,
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        color: textColor, // Color oscuro corregido (Nombres de clientes)
                        font: {
                            family: "'Inter', sans-serif",
                            weight: 'bold'
                        }
                    }
                }
            },
            layout: { padding: 0 }
        }
    });
}