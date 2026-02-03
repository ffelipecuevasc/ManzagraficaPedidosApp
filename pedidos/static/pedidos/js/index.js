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
   10. LÓGICA DE ÍTEMS DEL PEDIDO (CORREGIDO)
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
    const inputVentaTotal = document.getElementById('id_valor_venta');

    // Estado local de los ítems
    let items = [];

    // A. LÓGICA DE PRECIO AUTOMÁTICO (ROBUSTA)
    $selectProd.on('select2:select', function(e) {
        // Accedemos directamente al elemento <option> original a través del evento
        const element = e.params.data.element;
        // Leemos el atributo data-precio (jQuery lo parsea automáticamente)
        const precio = $(element).data('precio');

        // Validamos que precio no sea undefined (admitimos 0 como valor válido)
        if (precio !== undefined && precio !== null) {
            inputPrecio.value = precio;
        } else {
            inputPrecio.value = ''; // Limpiar si no hay precio
        }

        // Efecto visual opcional: resaltar el campo precio
        inputPrecio.classList.add('bg-yellow-50', 'transition-colors');
        setTimeout(() => inputPrecio.classList.remove('bg-yellow-50'), 500);
    });

    // B. Función Agregar Ítem
    btnAgregar.addEventListener('click', function() {
        const prodId = $selectProd.val();

        // Validación de seguridad para obtener el texto
        const selection = $selectProd.select2('data');
        const prodNombre = selection && selection.length > 0 ? selection[0].text : '';

        const cantidad = parseInt(inputCant.value) || 1;
        const precio = parseInt(inputPrecio.value) || 0;

        if (!prodId) {
            // Usamos tu alerta global si está disponible, sino alert normal
            if(window.showGlobalAlert) {
                showGlobalAlert('Falta información', 'Por favor selecciona un producto de la lista.');
            } else {
                alert("Por favor selecciona un producto.");
            }
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
    window.renderTable = function() {
        tableBody.innerHTML = '';
        let totalAcumulado = 0;

        if (items.length === 0) {
            if(rowEmpty) tableBody.appendChild(rowEmpty);
        } else {
            items.forEach((item, index) => {
                totalAcumulado += item.subtotal;

                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 dark:hover:bg-neutral-800/50 transition-colors border-b border-slate-100 dark:border-neutral-800 last:border-0";
                tr.innerHTML = `
                    <td class="px-4 py-3 font-medium text-slate-700 dark:text-slate-200">${item.nombre}</td>
                    <td class="px-4 py-3 text-center text-slate-600 dark:text-slate-400">${item.cantidad}</td>
                    <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">$${item.precio_unitario.toLocaleString('es-CL')}</td>
                    <td class="px-4 py-3 text-right font-bold text-slate-900 dark:text-white">$${item.subtotal.toLocaleString('es-CL')}</td>
                    <td class="px-4 py-3 text-center">
                        <button type="button" onclick="eliminarItem(${index})" class="p-1 text-slate-400 hover:text-red-500 transition-colors rounded-full hover:bg-red-50 dark:hover:bg-red-900/20">
                            <span class="material-icons-round text-lg">delete</span>
                        </button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }

        // Actualizar Totales Visuales
        cellTotal.innerText = '$' + totalAcumulado.toLocaleString('es-CL');

        // Actualizar JSON para Backend
        inputJson.value = JSON.stringify(items);

        // AUTO-LLENAR el campo "Valor Venta" del formulario original de Django
        if(inputVentaTotal) {
            inputVentaTotal.value = totalAcumulado;
            // Disparar evento para validaciones
            inputVentaTotal.dispatchEvent(new Event('input'));
        }
    };

    // D. Eliminar Ítem
    window.eliminarItem = function(index) {
        items.splice(index, 1);
        renderTable();
    };

    // E. Resetear el mini-formulario
    function resetForm() {
        $selectProd.val(null).trigger('change');
        inputCant.value = 1;
        inputPrecio.value = '';
    }

    // F. Lógica de "Crear Producto Rápido" (API)
    const btnToggle = document.getElementById('btn-toggle-crear-producto');
    const divFormProd = document.getElementById('form-crear-producto-rapido');
    const btnCancelProd = document.getElementById('btn-cancelar-prod');
    const btnSaveProd = document.getElementById('btn-guardar-prod-api');

    if(btnToggle) {
        btnToggle.addEventListener('click', () => {
            divFormProd.classList.remove('hidden');
            // Auto focus al nombre
            setTimeout(() => document.getElementById('new_prod_nombre').focus(), 100);
        });
    }

    if(btnCancelProd) {
        btnCancelProd.addEventListener('click', () => {
            divFormProd.classList.add('hidden');
        });
    }

    if(btnSaveProd) {
        btnSaveProd.addEventListener('click', function() {
            const nombre = document.getElementById('new_prod_nombre').value;
            const precio = document.getElementById('new_prod_precio').value;
            const url = this.getAttribute('data-url');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            if(!nombre) {
                alert("El nombre del producto es obligatorio");
                return;
            }

            const originalText = this.innerHTML;
            this.innerHTML = '<span class="material-icons-round animate-spin text-sm mr-2">refresh</span> Guardando...';
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
                    // Crear opción y seleccionarla
                    const newOption = new Option(data.nombre, data.id, true, true);

                    // IMPORTANTE: Escribir el atributo en el DOM para consistencia
                    $(newOption).attr('data-precio', data.precio);
                    $(newOption).data('precio', data.precio); // También en caché de jQuery

                    $selectProd.append(newOption).trigger('change');

                    // Llenar el input de precio manualmente
                    inputPrecio.value = data.precio;

                    // Limpiar y ocultar
                    divFormProd.classList.add('hidden');
                    document.getElementById('new_prod_nombre').value = '';
                    document.getElementById('new_prod_precio').value = '';
                } else {
                    alert("Error: " + JSON.stringify(data.errors));
                }
            })
            .catch(err => {
                console.error(err);
                alert("Error de conexión al crear producto");
            })
            .finally(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            });
        });
    }
}