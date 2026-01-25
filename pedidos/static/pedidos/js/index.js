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

    // E. Gráficos del Dashboard (ELIMINADO - Ahora es HTML/CSS puro)
    // if (document.getElementById('chartEstados')) {
    //    initDashboardCharts();
    // }

    // F. Modales de Detalle
    if (document.getElementById('modal-confirmacion')) {
        initDetailModals();
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
                    e.preventDefault();
                    var bufferText = '';
                    if (e.originalEvent && e.originalEvent.clipboardData) {
                        bufferText = e.originalEvent.clipboardData.getData('text/plain');
                    } else if (window.clipboardData) {
                        bufferText = window.clipboardData.getData('Text');
                    }

                    if (bufferText && bufferText.trim().length > 0) {
                        $('#id_detalles_pedido').summernote('insertText', bufferText);
                    } else {
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
    initMoneyValidation();
}

/* =========================================
   5. ORDENAMIENTO DE TABLAS
   ========================================= */
function initTableSorting() {
    const headers = document.querySelectorAll('th.sortable');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const sortField = header.getAttribute('data-sort');
            const currentUrl = new URL(window.location.href);
            const currentSort = currentUrl.searchParams.get('orden');
            let newSort = sortField;

            if (currentSort === sortField) {
                newSort = '-' + sortField;
            }
            currentUrl.searchParams.set('orden', newSort);
            window.location.href = currentUrl.toString();
        });
    });
}

/* =========================================
   7. VALIDACIÓN MONETARIA EN VIVO
   ========================================= */
function initMoneyValidation() {
    const inputVenta = document.getElementById('id_valor_venta');
    const inputAbono = document.getElementById('id_valor_abonado');
    const btnSubmit = document.getElementById('btn-submit-pedido');

    function validarMontos() {
        if (!inputVenta || !inputAbono) return;

        const venta = parseFloat(inputVenta.value) || 0;
        const abono = parseFloat(inputAbono.value) || 0;

        inputAbono.classList.remove('border-red-500', 'focus:ring-red-500');
        let errorMsg = document.getElementById('error-monto-js');
        if (errorMsg) errorMsg.remove();

        if (abono > venta) {
            inputAbono.classList.add('border-red-500', 'focus:ring-red-500');
            const p = document.createElement('p');
            p.id = 'error-monto-js';
            p.className = 'text-red-500 text-xs mt-1 font-bold flex items-center animate-pulse';
            p.innerHTML = '<span class="material-icons-round text-sm mr-1">cancel</span> El abono no puede ser mayor al valor total del pedido.';
            inputAbono.parentNode.appendChild(p);

            if(btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.classList.add('opacity-50', 'cursor-not-allowed', 'grayscale');
            }
        } else {
            if(btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.classList.remove('opacity-50', 'cursor-not-allowed', 'grayscale');
            }
        }
    }

    if (inputVenta && inputAbono) {
        inputVenta.addEventListener('input', validarMontos);
        inputAbono.addEventListener('input', validarMontos);
        inputAbono.addEventListener('keyup', validarMontos);
        inputAbono.addEventListener('change', validarMontos);
    }
}

/* =========================================
   8. LOGICA DE MODALES DE CONFIRMACIÓN (NUEVO)
   ========================================= */
function initDetailModals() {
    const modal = document.getElementById('modal-confirmacion');
    if (!modal) return;

    const titulo = document.getElementById('modal-titulo');
    const mensaje = document.getElementById('modal-mensaje');
    const btnConfirmar = document.getElementById('modal-btn-confirmar');
    const btnCancelar = document.getElementById('modal-btn-cancelar');

    // 1. Abrir Modal (Delegación para botones con data-confirm="true")
    const triggers = document.querySelectorAll('[data-confirm="true"]');
    triggers.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const tipo = this.getAttribute('data-type');

            // Configurar contenido
            if (tipo === 'TERMINAR') {
                titulo.textContent = '¿Finalizar y Pagar Pedido?';
                mensaje.innerHTML = 'Estás a punto de marcar este trabajo como <strong>TERMINADO</strong>.<br><br>El sistema registrará automáticamente que el <strong>TOTAL HA SIDO PAGADO ($0 deuda)</strong>.<br>¿Confirmas esta acción?';
                btnConfirmar.className = "inline-flex w-full justify-center rounded-lg bg-green-600 hover:bg-green-700 px-3 py-2 text-sm font-bold text-white shadow-sm sm:ml-3 sm:w-auto transition-colors uppercase tracking-wide";
            } else if (tipo === 'CLONAR') {
                titulo.textContent = '¿Reabrir Pedido?';
                mensaje.innerHTML = 'Se creará un <strong>NUEVO PEDIDO</strong> idéntico a este, con estado PENDIENTE y deuda inicial.<br><br>El pedido actual no se modificará y quedará guardado en la BD.';
                btnConfirmar.className = "inline-flex w-full justify-center rounded-lg bg-primary hover:bg-yellow-400 px-3 py-2 text-sm font-bold text-black shadow-sm sm:ml-3 sm:w-auto transition-colors uppercase tracking-wide";
            }

            btnConfirmar.href = url;
            modal.classList.remove('hidden');
        });
    });

    // 2. Cerrar Modal
    function closeModal() {
        modal.classList.add('hidden');
    }

    if(btnCancelar) {
        btnCancelar.addEventListener('click', closeModal);
    }
}