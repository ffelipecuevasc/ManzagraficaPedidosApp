/* =========================================
   1. INICIALIZACIÓN GLOBAL (Se ejecuta al cargar)
   ========================================= */
document.addEventListener('DOMContentLoaded', function () {
    // A. Gestión del Modo Oscuro
    initThemeToggle();

    // B. Inicializar Plugins
    initPlugins();

    // C. Formulario Pedidos / Cotizaciones
    // (Usamos el mismo ID 'pedidoForm' para ambos casos para reutilizar lógica)
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

    // G. Efecto acordeón de la Barra de Navegación Lateral
    initSidebarAccordions();
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
        themeToggleBtn.addEventListener('click', function () {
            if (htmlElement.classList.contains('dark')) {
                htmlElement.classList.remove('dark');
                localStorage.setItem('color-theme', 'light');
            } else {
                htmlElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
            }

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
    if ($('.select2').length) {
        $('.select2').select2({
            width: '100%',
            placeholder: "Seleccione una opción...",
            allowClear: true,
            language: {
                noResults: function () {
                    return "No se encontraron resultados";
                }
            }
        });
    }

    if ($('.summernote-editor').length) {
        let isDark = document.documentElement.classList.contains('dark');

        $('.summernote-editor').summernote({
            placeholder: 'Escribe aquí las especificaciones (Solo texto, no imágenes)...',
            tabsize: 2,
            height: 200,
            disableDragAndDrop: true,
            toolbar: [
                ['style', ['bold', 'italic', 'clear']],
                ['para', ['ul', 'ol']]
            ],
            callbacks: {
                onInit: function () {
                    if (isDark) {
                        $('.note-editable').css({'background-color': '#262626', 'color': 'white'});
                        $('.note-editor').css({'border-color': '#404040'});
                    }
                },
                onImageUpload: function (files) {
                    showGlobalAlert(
                        'No se permiten imágenes aquí',
                        'Para mantener el sistema rápido, por favor sube las imágenes en el campo <strong>"Imagen de Referencia"</strong> o envíalas por correo/WhatsApp.'
                    );
                },
                onPaste: function (e) {
                    var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('text/plain');
                    if (bufferText) {
                        e.preventDefault();
                        setTimeout(function () {
                            document.execCommand('insertText', false, bufferText);
                        }, 10);
                    } else {
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
   4. LÓGICA DEL FORMULARIO (PEDIDOS Y COTIZACIONES)
   ========================================= */
function initPedidoForm() {
    const $selectCliente = $('#id_cliente');

    const sectionProductos = document.getElementById('section-productos');
    const sectionDetalles = document.getElementById('section-detalles-pedido');
    const tituloTabla = document.getElementById('titulo-tabla-items');

    const sectionBuscar = document.getElementById('section-buscar-cliente');
    const sectionCrear = document.getElementById('section-crear-cliente');
    const btnToggleCrear = document.getElementById('btn-toggle-crear');
    const btnCancelarCrear = document.getElementById('btn-cancelar-crear');
    const btnGuardarApi = document.getElementById('btn-guardar-cliente-api');

    function checkClienteSeleccionado() {
        const clienteId = $selectCliente.val();

        // DETECCIÓN DE CONTEXTO: ¿Es Cotización o Pedido?
        // Si existe el campo "validez" (propio de cotización), cambiamos el texto.
        const isCotizacion = document.querySelector('[name="validez"]');
        const tipoDoc = isCotizacion ? "Cotización" : "Pedido";

        if (clienteId) {
            const nombreCliente = $("#id_cliente option:selected").text().trim();

            // Texto dinámico según el tipo de documento
            if (tituloTabla) {
                tituloTabla.innerHTML = `
                    <span class="material-icons-round text-primary text-base mr-2">list_alt</span>
                    Productos en ${tipoDoc} para: <span class="text-primary font-bold ml-1">${nombreCliente}</span>
                `;
            }

            if (sectionProductos) {
                sectionProductos.classList.remove('hidden');
                setTimeout(() => {
                    sectionProductos.classList.remove('opacity-0');
                }, 50);
            }
            if (sectionDetalles) {
                sectionDetalles.classList.remove('hidden');
                setTimeout(() => {
                    sectionDetalles.classList.remove('opacity-0');
                }, 300);
            }
        } else {
            if (sectionProductos) {
                sectionProductos.classList.add('opacity-0');
                setTimeout(() => sectionProductos.classList.add('hidden'), 500);
            }
            if (sectionDetalles) {
                sectionDetalles.classList.add('opacity-0');
                setTimeout(() => sectionDetalles.classList.add('hidden'), 500);
            }
        }
    }

    $selectCliente.on('change', checkClienteSeleccionado);
    checkClienteSeleccionado();

    if (btnToggleCrear) {
        btnToggleCrear.addEventListener('click', () => {
            sectionBuscar.classList.add('hidden');
            sectionCrear.classList.remove('hidden');
        });
    }

    if (btnCancelarCrear) {
        btnCancelarCrear.addEventListener('click', () => {
            sectionCrear.classList.add('hidden');
            sectionBuscar.classList.remove('hidden');
            document.getElementById('cliente-api-error').classList.add('hidden');
        });
    }

    if (btnGuardarApi) {
        btnGuardarApi.addEventListener('click', function () {
            const nombre = document.getElementById('new_client_nombre').value;
            const telefono = document.getElementById('new_client_telefono').value;
            const email = document.getElementById('new_client_email').value;

            if (!nombre || !telefono) {
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
                body: new URLSearchParams({'nombre': nombre, 'telefono': telefono, 'email': email})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
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
    // Nota: En Cotizaciones, 'id_valor_abonado' no existe, así que esta función
    // retornará de inmediato (return), lo cual es el comportamiento deseado.
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
            p.innerHTML = '<span class="material-icons-round text-sm mr-1">cancel</span> El abono no puede ser mayor al valor total.';
            inputAbono.parentNode.appendChild(p);

            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.classList.add('opacity-50', 'cursor-not-allowed', 'grayscale');
            }
        } else {
            if (btnSubmit) {
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

    const triggers = document.querySelectorAll('[data-confirm="true"]');
    triggers.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const tipo = this.getAttribute('data-type');

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

    function closeModal() {
        modal.classList.add('hidden');
    }

    if (btnCancelar) {
        btnCancelar.addEventListener('click', closeModal);
    }
}

/* =========================================
   9. UTILIDAD: ALERTA GLOBAL
   ========================================= */
function showGlobalAlert(titulo, mensaje) {
    const modal = document.getElementById('modal-alerta-global');
    if (!modal) return;

    document.getElementById('modal-alerta-titulo').innerText = titulo;
    document.getElementById('modal-alerta-mensaje').innerHTML = mensaje;
    modal.classList.remove('hidden');

    const btnCerrar = document.getElementById('btn-cerrar-alerta');
    btnCerrar.onclick = function () {
        modal.classList.add('hidden');
    }
}

/* =========================================
   10. LÓGICA DE ÍTEMS DEL PEDIDO (FINAL UX MEJORADA - TABLA EDITABLE + VALIDACIÓN DECIMALES)
   ========================================= */
function initProductManager() {
    const $selectProd = $('#select-producto');
    const $bloqueDetalle = $('#bloque-detalle-item');
    const inputCant = document.getElementById('input-cantidad');
    const inputPrecio = document.getElementById('input-precio');
    const btnAgregar = document.getElementById('btn-agregar-item');
    const tableBody = document.querySelector('#tabla-items tbody');
    const rowEmpty = document.getElementById('row-empty');
    const cellTotal = document.getElementById('cell-total-pedido');
    const inputJson = document.getElementById('input-items-json');
    const inputVentaTotal = document.getElementById('id_valor_venta');

    let items = [];
    let unidadActual = '';       // Texto legible (Ej: "Metro Cuadrado")
    let codigoUnidadActual = ''; // Código interno (Ej: "METRO_CUADRADO" o "UNITARIO")

    // --- NUEVO: CARGAR DATOS SI ESTAMOS EDITANDO ---
    if (inputJson && inputJson.value) {
        try {
            items = JSON.parse(inputJson.value);
            setTimeout(() => {
                renderTable();
            }, 100);
        } catch (e) {
            console.error("Error al cargar ítems existentes:", e);
        }
    }

    // --- HELPER: OCULTAR Y LIMPIAR BLOQUE DETALLE ---
    function ocultarBloqueDetalle() {
        $selectProd.val(null).trigger('change');
        $bloqueDetalle.addClass('opacity-0');
        setTimeout(() => {
            $bloqueDetalle.addClass('hidden');
            inputCant.value = 1;
            inputPrecio.value = '';
            unidadActual = '';
            codigoUnidadActual = ''; // Limpiamos también el código
        }, 500);
    }

    // A. AUTO-POBLAR PRECIO Y UNIDAD (Y CAPTURAR CÓDIGO)
    $selectProd.on('select2:select', function (e) {
        if ($bloqueDetalle.hasClass('hidden')) {
            $bloqueDetalle.removeClass('hidden');
            setTimeout(() => $bloqueDetalle.removeClass('opacity-0'), 50);
        }

        const element = e.params.data.element;
        const precioRaw = $(element).attr('data-precio') || $(element).data('precio');

        // Capturamos el texto legible para la tabla
        unidadActual = $(element).attr('data-unidad') || $(element).data('unidad') || '-';

        // --- NUEVO: Capturamos el código interno para la validación ---
        codigoUnidadActual = $(element).attr('data-codigo-unidad') || '';

        if (precioRaw) {
            inputPrecio.value = parseInt(precioRaw);
            inputPrecio.classList.add('bg-green-50', 'transition-colors');
            setTimeout(() => inputPrecio.classList.remove('bg-green-50'), 500);
        } else {
            inputPrecio.value = '';
        }

        setTimeout(() => {
            if (inputPrecio.value) inputCant.focus();
            else inputPrecio.focus();
        }, 100);
    });

    $selectProd.on('select2:clear', function (e) {
        ocultarBloqueDetalle();
    });

    // B. SOPORTE TECLA ENTER
    if (inputCant && inputPrecio) {
        [inputCant, inputPrecio].forEach(input => {
            input.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    btnAgregar.click();
                }
            });
        });
    }

    // C. AGREGAR ÍTEM (CON VALIDACIÓN DE DECIMALES)
    if (btnAgregar) {
        btnAgregar.addEventListener('click', function () {
            const prodId = $selectProd.val();
            if (!prodId) {
                showGlobalAlert('Falta información', 'Por favor selecciona un producto de la lista.');
                return;
            }

            const selection = $selectProd.select2('data');
            const prodNombre = selection && selection.length > 0 ? selection[0].text : 'Producto';

            const cantidad = parseFloat(inputCant.value) || 0;
            const precio = parseInt(inputPrecio.value) || 0;

            if (cantidad <= 0) {
                showGlobalAlert('Cantidad Inválida', 'La cantidad debe ser mayor a 0.');
                return;
            }

            // --- VALIDACIÓN DE NEGOCIO: NO DECIMALES EN UNITARIO ---
            // Si la cantidad tiene decimales (el resto de dividir por 1 no es 0)
            if (cantidad % 1 !== 0) {
                // Y el producto es UNITARIO
                if (codigoUnidadActual === 'UNITARIO') {
                    showGlobalAlert(
                        'Cantidad Inválida',
                        `El producto <strong>${prodNombre}</strong> se vende por unidades.<br><br>No puedes ingresar cantidades decimales (como ${cantidad}) para este producto, solo números enteros.`
                    );
                    return;
                }
            }
            // -------------------------------------------------------

            items.push({
                producto_id: prodId,
                nombre: prodNombre,
                unidad: unidadActual,
                cantidad: cantidad,
                precio_unitario: precio,
                subtotal: Math.round(cantidad * precio)
            });

            renderTable();
            ocultarBloqueDetalle();
        });
    }

    // D. RENDERIZAR TABLA
    window.renderTable = function () {
        tableBody.innerHTML = '';
        let totalAcumulado = 0;

        if (items.length === 0) {
            if (rowEmpty) tableBody.appendChild(rowEmpty);
        } else {
            items.forEach((item, index) => {
                totalAcumulado += item.subtotal;

                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 dark:hover:bg-neutral-800/50 transition-colors border-b border-slate-100 dark:border-neutral-800 last:border-0";

                tr.innerHTML = `
                    <td class="px-4 py-3 font-medium text-slate-700 dark:text-slate-200">${item.nombre}</td>
                    <td class="px-4 py-3 text-center text-xs text-slate-500 font-mono bg-slate-50 dark:bg-neutral-800 rounded mx-2">${item.unidad}</td>
                    <td class="px-4 py-3 text-center text-slate-600 dark:text-slate-400 font-bold">${item.cantidad}</td>
                    
                    <td class="px-4 py-3 text-right w-32">
                        <div class="relative rounded-md shadow-sm">
                            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-2">
                                <span class="text-slate-400 sm:text-xs font-bold">$</span>
                            </div>
                            <input type="number" 
                                   class="block w-full rounded border-0 py-1.5 pl-6 pr-2 text-right text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6 dark:bg-neutral-800 dark:text-white dark:ring-neutral-700" 
                                   value="${item.precio_unitario}"
                                   onchange="updateItemPrice(${index}, this.value)"
                                   onkeydown="if(event.key === 'Enter') { this.blur(); event.preventDefault(); }"
                            >
                        </div>
                    </td>

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

        if (cellTotal) cellTotal.innerText = '$' + totalAcumulado.toLocaleString('es-CL');
        if (inputJson) inputJson.value = JSON.stringify(items);

        if (inputVentaTotal) {
            inputVentaTotal.value = totalAcumulado;
            inputVentaTotal.dispatchEvent(new Event('input'));
        }
    };

    // E. ACTUALIZAR PRECIO
    window.updateItemPrice = function (index, nuevoPrecio) {
        const precio = parseInt(nuevoPrecio) || 0;
        items[index].precio_unitario = precio;
        items[index].subtotal = Math.round(items[index].cantidad * precio);
        renderTable();
    };

    window.eliminarItem = function (index) {
        items.splice(index, 1);
        renderTable();
    };

    // F. CREAR PRODUCTO RÁPIDO (Lógica API)
    const btnToggle = document.getElementById('btn-toggle-crear-producto');
    const divFormProd = document.getElementById('form-crear-producto-rapido');
    const btnCancelProd = document.getElementById('btn-cancelar-prod');
    const btnSaveProd = document.getElementById('btn-guardar-prod-api');

    if (btnToggle) {
        btnToggle.addEventListener('click', () => {
            divFormProd.classList.remove('hidden');
            setTimeout(() => document.getElementById('new_prod_nombre').focus(), 100);
        });
    }

    if (btnCancelProd) {
        btnCancelProd.addEventListener('click', () => {
            divFormProd.classList.add('hidden');
        });
    }

    if (btnSaveProd) {
        btnSaveProd.addEventListener('click', function () {
            const nombre = document.getElementById('new_prod_nombre').value;
            const precio = document.getElementById('new_prod_precio').value;
            const unidad = document.getElementById('new_prod_unidad').value;

            const url = this.getAttribute('data-url');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            if (!nombre) {
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
                    'valor_neto': precio || 0,
                    'unidad': unidad,
                    'descripcion': 'Creado desde Pedido Rápido'
                })
            })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const newOption = new Option(data.nombre, data.id, true, true);

                        $(newOption).attr('data-precio', data.precio);
                        $(newOption).data('precio', data.precio);

                        $(newOption).attr('data-unidad', data.unidad); // Texto
                        $(newOption).data('unidad', data.unidad);

                        // Aseguramos que el producto rápido también tenga su código (asumimos que viene del backend o lo inferimos)
                        // Nota: Para productos rápidos creados al vuelo, idealmente el backend debe devolver el código también.
                        // Por ahora, como el select de "crear rápido" tiene values en mayúsculas (UNITARIO), podemos usar eso.
                        $(newOption).attr('data-codigo-unidad', unidad);

                        $selectProd.append(newOption).trigger('change');

                        $selectProd.trigger({
                            type: 'select2:select',
                            params: {
                                data: {
                                    element: newOption,
                                    id: data.id,
                                    text: data.nombre
                                }
                            }
                        });

                        divFormProd.classList.add('hidden');
                        document.getElementById('new_prod_nombre').value = '';
                        document.getElementById('new_prod_precio').value = '';
                        document.getElementById('new_prod_unidad').value = 'UNITARIO';
                    } else {
                        alert("Error: " + JSON.stringify(data.errors));
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert("Error de conexión");
                })
                .finally(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                });
        });
    }
}

/* =========================================
   11. LÓGICA ACORDEONES SIDEBAR (NUEVO)
   ========================================= */
function initSidebarAccordions() {
    console.log("Iniciando Acordeones..."); // <--- AGREGA ESTA LÍNEA PARA VERIFICAR

    const triggers = document.querySelectorAll('.btn-accordion');

    if (triggers.length === 0) {
        console.warn("No se encontraron botones de acordeón (.btn-accordion)");
        return;
    }

    // 1. Manejo del Click
    triggers.forEach(btn => {
        btn.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const content = document.querySelector(targetId);
            const icon = this.querySelector('.chevron-icon');

            // Toggle visibilidad
            content.classList.toggle('hidden');

            // Rotar icono (clase rotate-180 de Tailwind o CSS estándar)
            if (content.classList.contains('hidden')) {
                icon.classList.remove('rotate-180');
                // Opcional: quitar color activo al título si se cierra
                this.classList.remove('text-primary');
            } else {
                icon.classList.add('rotate-180');
                // Opcional: dar color al título si se abre
                // this.classList.add('text-primary');
            }
        });
    });

    // 2. Auto-apertura basada en la URL actual (Mejora UX)
    // Buscamos el enlace que tiene la clase "text-primary" (el activo según Django)
    // Nota: Usamos contains porque Tailwind puede tener muchas clases.
    // En tu HTML pusiste: {% if ... %}text-primary font-bold{% endif %}

    const activeLink = document.querySelector('.accordion-content a.text-primary');

    if (activeLink) {
        // Encontramos el contenedor padre (el div hidden)
        const parentAccordion = activeLink.closest('.accordion-content');
        if (parentAccordion) {
            // Lo abrimos
            parentAccordion.classList.remove('hidden');

            // Buscamos el botón que controla este acordeón para rotar su icono
            const targetId = '#' + parentAccordion.id;
            const correspondingBtn = document.querySelector(`[data-target="${targetId}"]`);

            if (correspondingBtn) {
                const icon = correspondingBtn.querySelector('.chevron-icon');
                if (icon) icon.classList.add('rotate-180');
                // correspondingBtn.classList.add('text-primary'); // Opcional
            }
        }
    }
}