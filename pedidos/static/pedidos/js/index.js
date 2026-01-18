/* =========================================
   1. INICIALIZACIÓN GLOBAL (Se ejecuta al cargar)
   ========================================= */
document.addEventListener('DOMContentLoaded', function() {

    // A. Gestión del Modo Oscuro (Funciona para Login y Dashboard)
    initThemeToggle();

    // B. Inicializar Plugins (Select2 y Summernote)
    initPlugins();

    // C. Lógica Específica del Formulario de Pedidos
    // Solo se ejecuta si existe el formulario en la página
    if (document.getElementById('pedidoForm')) {
        initPedidoForm();
    }
});


/* =========================================
   2. FUNCIONES DE TEMA (MODO OSCURO)
   ========================================= */
function initThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Verificar preferencia guardada al inicio
    const isDark = localStorage.getItem('color-theme') === 'dark' ||
                   (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);

    if (isDark) {
        htmlElement.classList.add('dark');
    } else {
        htmlElement.classList.remove('dark');
    }

    // Evento Click (si el botón existe en esta vista)
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            if (htmlElement.classList.contains('dark')) {
                htmlElement.classList.remove('dark');
                localStorage.setItem('color-theme', 'light');
            } else {
                htmlElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
            }
            // Reinicializar Summernote si existe para cambiar su color
            if ($('#id_detalles_pedido').length) {
                // Pequeño hack para refrescar estilos de summernote
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
    // Select2 (Buscador desplegable)
    if ($('.select2').length) {
        $('.select2').select2({
            width: '100%',
            placeholder: "Seleccione una opción...",
            allowClear: true
        });
    }

    // Summernote (Editor de texto enriquecido)
    if ($('#id_detalles_pedido').length) {
        let isDark = document.documentElement.classList.contains('dark');

        $('#id_detalles_pedido').summernote({
            placeholder: 'Escribe aquí las especificaciones...',
            tabsize: 2,
            height: 200,
            toolbar: [['style', ['bold', 'italic', 'clear']], ['para', ['ul', 'ol']]],
            callbacks: {
                onInit: function() {
                    // Ajuste manual de colores para modo oscuro
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

    // Botones
    const btnToggleCrear = document.getElementById('btn-toggle-crear');
    const btnCancelarCrear = document.getElementById('btn-cancelar-crear');
    const btnGuardarApi = document.getElementById('btn-guardar-cliente-api');

    // --- 4.1 Mostrar/Ocultar Wizard ---
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
    checkClienteSeleccionado(); // Check inicial

    // --- 4.2 Alternar entre Buscar y Crear ---
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

    // --- 4.3 AJAX: Guardar Cliente Rápido ---
    if (btnGuardarApi) {
        btnGuardarApi.addEventListener('click', function() {
            // A. Obtener datos
            const nombre = document.getElementById('new_client_nombre').value;
            const telefono = document.getElementById('new_client_telefono').value;
            const email = document.getElementById('new_client_email').value;

            // Validación simple
            if(!nombre || !telefono) {
                const errorDiv = document.getElementById('cliente-api-error');
                errorDiv.innerText = 'Nombre y Teléfono son obligatorios';
                errorDiv.classList.remove('hidden');
                return;
            }

            // B. UX: Botón cargando
            const originalText = btnGuardarApi.innerHTML;
            btnGuardarApi.disabled = true;
            btnGuardarApi.innerHTML = '<span class="material-icons-round animate-spin text-sm mr-2">refresh</span> Guardando...';

            // C. Obtener Datos "Invisibles" del HTML (Data Attributes y Token)
            const apiUrl = btnGuardarApi.getAttribute('data-url'); // <--- AQUÍ ESTÁ LA MAGIA
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Robamos el token del formulario principal

            // D. La Petición Fetch
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
                    // Éxito: Agregamos la opción al Select2 y la seleccionamos
                    const newOption = new Option(data.nombre, data.id, true, true);
                    $selectCliente.append(newOption).trigger('change');

                    // Reseteamos vista
                    sectionCrear.classList.add('hidden');
                    sectionBuscar.classList.remove('hidden');
                    document.getElementById('new_client_nombre').value = '';
                    document.getElementById('new_client_telefono').value = '';
                    document.getElementById('new_client_email').value = '';

                    checkClienteSeleccionado();
                } else {
                    // Error del servidor (ej: validación)
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