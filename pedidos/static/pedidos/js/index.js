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
        initProductManager();
    }

    // D. Ordenamiento Tablas
    if (document.querySelector('th.sortable')) {
        initTableSorting();
    }

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

            // ACTUALIZACIÓN: Destruir y recrear Summernote buscando por CLASE
            if ($('.summernote-editor').length) {
                $('.summernote-editor').summernote('destroy');
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

    // B. Configuración Summernote (Editor de Texto) - MEJORADO CON MODAL
    if ($('.summernote-editor').length) {
        let isDark = document.documentElement.classList.contains('dark');

        $('.summernote-editor').summernote({
            placeholder: 'Escribe aquí las especificaciones (Solo texto, no imágenes)...',
            tabsize: 2,
            height: 200,
            disableDragAndDrop: true, // Deshabilita arrastrar archivos
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
                // CANDADO 1: Bloqueo de subida directa (Botón Imagen)
                onImageUpload: function(files) {
                    showGlobalAlert(
                        'No se permiten imágenes aquí',
                        'Para mantener el sistema rápido, por favor sube las imágenes en el campo <strong>"Imagen de Referencia"</strong> o envíalas por correo/WhatsApp.'
                    );
                },
                // CANDADO 2: Bloqueo de Pegado (Ctrl+V) de imágenes
                onPaste: function (e) {
                    var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('text/plain');

                    // Si hay texto plano, permitimos pegar (pero limpiamos formato)
                    if (bufferText) {
                        e.preventDefault();
                        // Esperamos un momento para insertar solo el texto limpio
                        setTimeout(function(){
                            document.execCommand('insertText', false, bufferText);
                        }, 10);
                    } else {
                        // Si no es texto (es imagen o archivo rico), bloqueamos y mostramos modal
                        e.preventDefault();
                        showGlobalAlert(
                            'Pegado de imágenes bloqueado',
                            'El editor solo acepta texto. <br><br>Si intentas pegar una imagen, por favor usa el campo <strong>"Imagen de Referencia"</strong>.'
                        );
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
   8. LOGICA DE MODALES DE CONFIRMACIÓN
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

/* =========================================
   9. UTILIDAD: ALERTA GLOBAL (NUEVO)
   ========================================= */
function showGlobalAlert(titulo, mensaje) {
    const modal = document.getElementById('modal-alerta-global');
    if(!modal) return; // Si no está en el HTML, no hacemos nada (fallback silencioso)

    document.getElementById('modal-alerta-titulo').innerText = titulo;
    document.getElementById('modal-alerta-mensaje').innerHTML = mensaje;

    modal.classList.remove('hidden');

    // Configurar cierre
    const btnCerrar = document.getElementById('btn-cerrar-alerta');
    btnCerrar.onclick = function() {
        modal.classList.add('hidden');
    }
}

/* =========================================
   10. LÓGICA DE ÍTEMS DEL PEDIDO (NUEVO)
   ========================================= */
function initProductManager() {
    const $selectProd = $('#select-producto');
    const inputCant = document.getElementById('input-cantidad');
    const inputPrecio = document.getElementById('input-precio');
    const btnAgregar = document.getElementById('btn-agregar-item');
    const tableBody = document.querySelector('#tabla-items tbody');
    const rowEmpty = document.getElementById('row-empty');
    const cellTotal = document.getElementById('cell-total-pedido');
    const inputJson = document.getElementById('input-items-json');
    const inputVentaTotal = document.getElementById('id_valor_venta'); // El campo del Formulario Django

    // Estado local de los ítems
    let items = [];

    // A. Al seleccionar producto, poner precio sugerido
    $selectProd.on('select2:select', function(e) {
        const precio = $(this).find(':selected').data('precio');
        if(precio) inputPrecio.value = precio;
    });

    // B. Función Agregar Ítem
    btnAgregar.addEventListener('click', function() {
        const prodId = $selectProd.val();
        const prodNombre = $selectProd.find(':selected').text();
        const cantidad = parseInt(inputCant.value) || 1;
        const precio = parseInt(inputPrecio.value) || 0;

        if (!prodId) {
            alert("Por favor selecciona un producto.");
            return;
        }

        // Agregar al array
        items.push({
            producto_id: prodId,
            nombre: prodNombre,
            cantidad: cantidad,
            precio_unitario: precio,
            subtotal: cantidad * precio
        });

        renderTable();
        resetForm();
    });

    // C. Renderizar Tabla
    window.renderTable = function() { // Global para poder llamar desde eliminar
        tableBody.innerHTML = '';
        let totalAcumulado = 0;

        if (items.length === 0) {
            if(rowEmpty) tableBody.appendChild(rowEmpty);
        } else {
            items.forEach((item, index) => {
                totalAcumulado += item.subtotal;

                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 dark:hover:bg-neutral-800/50 transition-colors";
                tr.innerHTML = `
                    <td class="px-4 py-3 font-medium">${item.nombre}</td>
                    <td class="px-4 py-3 text-center">${item.cantidad}</td>
                    <td class="px-4 py-3 text-right">$${item.precio_unitario.toLocaleString('es-CL')}</td>
                    <td class="px-4 py-3 text-right font-bold">$${item.subtotal.toLocaleString('es-CL')}</td>
                    <td class="px-4 py-3 text-center">
                        <button type="button" onclick="eliminarItem(${index})" class="text-red-400 hover:text-red-600">
                            <span class="material-icons-round text-lg">delete</span>
                        </button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }

        // Actualizar Totales Visuales y Inputs
        cellTotal.innerText = '$' + totalAcumulado.toLocaleString('es-CL');

        // Actualizar JSON para Backend
        inputJson.value = JSON.stringify(items);

        // AUTO-LLENAR el campo "Valor Venta" del formulario original de Django
        if(inputVentaTotal) {
            inputVentaTotal.value = totalAcumulado;
            // Disparar evento para que se valide el abono si ya estaba escrito
            inputVentaTotal.dispatchEvent(new Event('input'));
        }
    };

    // D. Eliminar Ítem (Global)
    window.eliminarItem = function(index) {
        items.splice(index, 1);
        renderTable();
    };

    // E. Resetear el mini-formulario
    function resetForm() {
        $selectProd.val(null).trigger('change');
        inputCant.value = 1;
        inputPrecio.value = '';
        inputPrecio.placeholder = '0';
    }

    // F. Lógica de "Crear Producto Rápido" (API)
    const btnToggle = document.getElementById('btn-toggle-crear-producto');
    const divFormProd = document.getElementById('form-crear-producto-rapido');
    const btnCancelProd = document.getElementById('btn-cancelar-prod');
    const btnSaveProd = document.getElementById('btn-guardar-prod-api');

    btnToggle.addEventListener('click', () => {
        divFormProd.classList.remove('hidden');
    });

    btnCancelProd.addEventListener('click', () => {
        divFormProd.classList.add('hidden');
    });

    btnSaveProd.addEventListener('click', function() {
        const nombre = document.getElementById('new_prod_nombre').value;
        const precio = document.getElementById('new_prod_precio').value;
        const url = this.getAttribute('data-url');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        if(!nombre) return alert("El nombre es obligatorio");

        // UI Loading
        const originalText = this.innerHTML;
        this.innerHTML = 'Guardando...';
        this.disabled = true;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'nombre': nombre,
                'precio_venta': precio || 0,
                'descripcion': 'Creado desde Pedido Rápido'
            })
        })
        .then(r => r.json())
        .then(data => {
            if(data.success) {
                // Agregar al select y seleccionarlo
                const newOption = new Option(data.nombre, data.id, true, true);
                // Guardar el precio en el data-attribute para que funcione la autoselección
                $(newOption).data('precio', data.precio);

                $selectProd.append(newOption).trigger('change');

                // Disparar manualmente el evento de selección para que se llene el precio
                inputPrecio.value = data.precio;

                // Limpiar y ocultar
                divFormProd.classList.add('hidden');
                document.getElementById('new_prod_nombre').value = '';
                document.getElementById('new_prod_precio').value = '';
            } else {
                alert("Error: " + JSON.stringify(data.errors));
            }
        })
        .catch(err => console.error(err))
        .finally(() => {
            this.innerHTML = originalText;
            this.disabled = false;
        });
    });
}