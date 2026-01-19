/* =========================================
   1. INICIALIZACIÓN GLOBAL (Se ejecuta al cargar)
   ========================================= */
document.addEventListener('DOMContentLoaded', function() {

    // A. Gestión del Modo Oscuro
    initThemeToggle();

    // B. Inicializar Plugins (Select2 y Summernote)
    initPlugins();

    // C. Lógica del Formulario de Pedidos (Solo si existe)
    if (document.getElementById('pedidoForm')) {
        initPedidoForm();
    }

    // D. Lógica de Ordenamiento de Tablas (NUEVO)
    // Solo si existen columnas ordenables
    if (document.querySelector('th.sortable')) {
        initTableSorting();
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
    if ($('.select2').length) {
        $('.select2').select2({
            width: '100%',
            placeholder: "Seleccione una opción...",
            allowClear: true
        });
    }

    if ($('#id_detalles_pedido').length) {
        let isDark = document.documentElement.classList.contains('dark');
        $('#id_detalles_pedido').summernote({
            placeholder: 'Escribe aquí las especificaciones...',
            tabsize: 2,
            height: 200,
            toolbar: [['style', ['bold', 'italic', 'clear']], ['para', ['ul', 'ol']]],
            callbacks: {
                onInit: function() {
                    if(isDark) {
                        $('.note-editable').css({'background-color': '#262626', 'color': 'white'});
                        $('.note-editor').css({'border-color': '#404040'});
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