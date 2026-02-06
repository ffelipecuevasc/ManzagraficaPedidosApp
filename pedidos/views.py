from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.template.loader import render_to_string
from django.db.models import ProtectedError
from .models import Pedido, Cliente, Cotizacion, Producto, ItemPedido, ItemCotizacion
from .forms import PedidoForm, ClienteForm, CotizacionForm, ProductoForm
from .decorators import transaccion_segura
from .utils import generar_respaldo_mysql, restaurar_bd_mysql
from datetime import timedelta, datetime
from PedidosApp import settings
import weasyprint
import json
import os

# ==========================================
# PANEL DE CONTROL
# ==========================================
@login_required
def dashboard(request):
    # ==========================================
    # 1. KPIs FINANCIEROS (Dinero)
    # ==========================================
    ingresos_totales = Pedido.objects.filter(estado='TERMINADO').aggregate(
        total=Sum('valor_venta')
    )['total'] or 0

    por_cobrar = Pedido.objects.filter(
        estado__in=['PENDIENTE', 'EN_PROCESO']
    ).aggregate(
        total=Sum(F('valor_venta') - F('valor_abonado'))
    )['total'] or 0

    # ==========================================
    # 2. MÉTRICAS OPERATIVAS
    # ==========================================
    total_clientes = Cliente.objects.count()

    total_pedidos = Pedido.objects.count()
    pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
    en_proceso = Pedido.objects.filter(estado='EN_PROCESO').count()
    completados = Pedido.objects.filter(estado='TERMINADO').count()

    # ==========================================
    # 3. CÁLCULOS PARA GRÁFICOS HTML (CSS PURO)
    # ==========================================

    # A. Datos para Gráfico de Dona (Conic Gradient)
    # Calculamos los puntos de corte del gradiente (acumulados)
    if total_pedidos > 0:
        pct_pendientes = (pendientes / total_pedidos) * 100
        pct_en_proceso = (en_proceso / total_pedidos) * 100
        # Puntos de parada para el CSS conic-gradient
        stop_1 = pct_pendientes
        stop_2 = pct_pendientes + pct_en_proceso
    else:
        stop_1 = 0
        stop_2 = 0

    # Porcentajes individuales para mostrar en texto
    pct_text_pendientes = round((pendientes / total_pedidos * 100)) if total_pedidos > 0 else 0
    pct_text_proceso = round((en_proceso / total_pedidos * 100)) if total_pedidos > 0 else 0
    pct_text_completados = round((completados / total_pedidos * 100)) if total_pedidos > 0 else 0

    # B. Datos para Gráfico de Barras (Top Clientes)
    top_clientes = Cliente.objects.annotate(
        num_pedidos=Count('pedido')
    ).order_by('-num_pedidos')[:5]

    # Obtener el valor máximo para calcular el ancho de las barras (width %)
    max_pedidos = top_clientes[0].num_pedidos if top_clientes else 1

    # ==========================================
    # 4. CONTEXTO
    # ==========================================
    context = {
        # KPIs
        'ingresos_totales': ingresos_totales,
        'por_cobrar': por_cobrar,
        'total_clientes': total_clientes,
        'total_pedidos': total_pedidos,  # Necesario para el centro de la dona

        # Datos Crudos
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'completados': completados,

        # Porcentajes Visuales (Donut)
        'donut_stop_1': stop_1,
        'donut_stop_2': stop_2,
        'pct_pendientes': pct_text_pendientes,
        'pct_proceso': pct_text_proceso,
        'pct_completados': pct_text_completados,

        # Datos Visuales (Barras)
        'top_clientes': top_clientes,
        'max_pedidos': max_pedidos,
    }

    return render(request, 'pedidos/dashboard.html', context)

# ==========================================
# GESTIÓN DE PEDIDOS
# ==========================================

@login_required
@transaccion_segura
def crear_pedido(request):
    cliente_form = ClienteForm()
    # Necesario para llenar el Select2 de productos en el HTML
    productos_disponibles = Producto.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)

        if form.is_valid():
            # 1. Guardar el Pedido (Padre)
            pedido = form.save()

            # 2. Procesar los Ítems (Hijos) desde el JSON oculto
            items_json = request.POST.get('items_json')

            if items_json:
                try:
                    data_items = json.loads(items_json)

                    for item in data_items:
                        # item es un dict: {'producto_id': '5', 'cantidad': 2, 'precio_unitario': 15000, ...}
                        producto_obj = Producto.objects.get(pk=item['producto_id'])

                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=producto_obj,
                            cantidad=float(item['cantidad']),
                            precio_unitario=int(item['precio_unitario'])
                        )
                except Exception as e:
                    # Si algo falla en el JSON, no rompemos el flujo principal,
                    # pero podrías loguear el error: print(f"Error guardando items: {e}")
                    pass

            # Redirigir al detalle del pedido recién creado
            return redirect('detalle_pedido', pk=pedido.pk)
    else:
        form = PedidoForm()

    context = {
        'form': form,
        'cliente_form': cliente_form,
        'productos_disponibles': productos_disponibles  # ¡Vital para que funcione el select!
    }

    return render(request, 'pedidos/pedido_form.html', context)

@login_required
@transaccion_segura
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    productos_disponibles = Producto.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            pedido = form.save()

            items_json = request.POST.get('items_json')
            if items_json:
                try:
                    pedido.items.all().delete() # Borrón
                    data_items = json.loads(items_json)
                    for item in data_items:
                        producto_obj = Producto.objects.get(pk=item['producto_id'])
                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=producto_obj,
                            cantidad=float(item['cantidad']),
                            precio_unitario=int(item['precio_unitario'])
                        )
                except Exception:
                    pass
            # Redirigir al detalle del pedido editado
            return redirect('detalle_pedido', pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)

    # --- NUEVO: PRE-CARGA DE ÍTEMS PARA EL FRONTEND ---
    items_list = []
    for item in pedido.items.all():
        items_list.append({
            'producto_id': item.producto.id,
            'nombre': item.producto.nombre,
            'unidad': item.producto.get_unidad_display(),
            'cantidad': float(item.cantidad),
            'precio_unitario': item.precio_unitario,
            'subtotal': int(round(item.cantidad * item.precio_unitario))
        })
    # --------------------------------------------------

    return render(request, 'pedidos/pedido_form.html', {
        'form': form,
        'productos_disponibles': productos_disponibles,
        'items_json': json.dumps(items_list) # ¡Aquí enviamos los datos al HTML!
    })

@login_required
@transaccion_segura
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        return redirect('dashboard')
    return render(request, 'pedidos/pedido_confirm_delete.html', {'pedido': pedido})

@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, 'pedidos/pedido_detail.html', {'pedido': pedido})


@login_required
def cambiar_estado_pedido(request, pk, nuevo_estado):
    pedido = get_object_or_404(Pedido, pk=pk)

    # Validar que el nuevo estado sea una opción válida
    opciones_validas = [opcion[0] for opcion in Pedido.ESTADO_CHOICES]

    if nuevo_estado in opciones_validas:
        # REGLA DE NEGOCIO: Si se termina, se asume pagado
        if nuevo_estado == 'TERMINADO':
            pedido.valor_abonado = pedido.valor_venta

        pedido.estado = nuevo_estado
        pedido.save()

    return redirect('detalle_pedido', pk=pk)

@login_required
def lista_pedidos(request):
    # Contadores globales
    total_pedidos = Pedido.objects.count()
    pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
    en_proceso = Pedido.objects.filter(estado='EN_PROCESO').count()
    completados = Pedido.objects.filter(estado='TERMINADO').count()

    # 1. Base QuerySet
    pedidos = Pedido.objects.all()

    # 2. Lógica de Ordenamiento (Sorting)
    orden = request.GET.get('orden', '-fecha_solicitud')  # Default: Lo más nuevo primero

    campos_permitidos = [
        'cliente__nombre', '-cliente__nombre',
        'estado', '-estado',
        'fecha_entrega', '-fecha_entrega',
        'fecha_solicitud', '-fecha_solicitud',
        'id', '-id'
    ]

    if orden in campos_permitidos:
        pedidos = pedidos.order_by(orden)
    else:
        pedidos = pedidos.order_by('-fecha_solicitud')

    # 3. Filtros Existentes (Estado)
    estado_filter = request.GET.get('estado')
    if estado_filter:
        pedidos = pedidos.filter(estado=estado_filter)

    # 4. Búsqueda - Solo Cliente y Teléfono
    busqueda = request.GET.get('busqueda')
    if busqueda:
        pedidos = pedidos.filter(
            Q(cliente__nombre__icontains=busqueda) |
            Q(cliente__telefono__icontains=busqueda)
        )

    # 5. Paginación
    paginator = Paginator(pedidos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_pedidos': total_pedidos,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'completados': completados,
        'pedidos': page_obj,
        'page_obj': page_obj,
        'busqueda': busqueda,
        'estado_filter': estado_filter,
        'orden': orden,
        'is_paginated': page_obj.has_other_pages(),
    }

    return render(request, 'pedidos/pedido_list.html', context)

@login_required
@transaccion_segura
def duplicar_pedido(request, pk):
    # 1. Obtener el pedido original
    original = get_object_or_404(Pedido, pk=pk)

    # 2. Crear una copia en memoria (sin PK para que sea nuevo)
    nuevo_pedido = Pedido(
        cliente=original.cliente,
        resumen_pedido=original.resumen_pedido,
        detalles_pedido=original.detalles_pedido,
        valor_venta=original.valor_venta,
        valor_abonado=0,  # IMPORTANTE: La deuda nace en 0
        estado='PENDIENTE',  # IMPORTANTE: Nace pendiente
        fecha_entrega=original.fecha_entrega,  # Mantenemos fecha ref, usuario editará si quiere
        imagen_referencia=original.imagen_referencia  # Mantenemos la imagen si tenía
    )

    # 3. Guardar el nuevo registro (esto genera fecha_solicitud actual automática)
    nuevo_pedido.save()

    # 4. Redirigir al detalle del nuevo pedido clonado
    return redirect('detalle_pedido', pk=nuevo_pedido.pk)

# ==========================================
# GESTIÓN DE CLIENTES
# ==========================================
@login_required
def lista_clientes(request):
    # Anotar clientes con el total de pedidos
    clientes = Cliente.objects.annotate(total_pedidos=Count('pedido'))
    
    # Búsqueda
    busqueda = request.GET.get('busqueda')
    if busqueda:
        clientes = clientes.filter(
            Q(nombre__icontains=busqueda) | 
            Q(email__icontains=busqueda) |
            Q(telefono__icontains=busqueda)
        )
    
    # Calcular clientes activos (aquellos con más de 0 pedidos)
    # Nota: Usamos la lista anotada para filtrar en Python o hacemos otra query.
    # Para eficiencia, podemos contar sobre el QuerySet anotado:
    clientes_activos = clientes.filter(total_pedidos__gt=0).count()
    
    # Obtener el cliente top (con más pedidos)
    top_cliente = clientes.order_by('-total_pedidos').first()
    
    context = {
        'clientes': clientes,
        'clientes_activos': clientes_activos,
        'clientes_nuevos': 0, # Placeholder
        'top_cliente': top_cliente,
        'busqueda': busqueda,
    }
    return render(request, 'pedidos/cliente_list.html', context)

@login_required
@transaccion_segura
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'pedidos/cliente_form.html', {'form': form})

@login_required
@transaccion_segura
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'pedidos/cliente_form.html', {'form': form})

@login_required
@transaccion_segura
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'pedidos/cliente_confirm_delete.html', {'cliente': cliente})

@login_required
@require_POST
def api_crear_cliente_rapido(request):
    form = ClienteForm(request.POST)
    if form.is_valid():
        cliente = form.save()
        return JsonResponse({
            'success': True,
            'id': cliente.id,
            'nombre': cliente.nombre,
            'telefono': cliente.telefono
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })

@login_required
def trabajo_semanal(request):
    # 1. Definir Fechas
    hoy = timezone.now().date()
    limite_semana = hoy + timedelta(days=7)

    # 2. Obtener Pedidos Activos
    activos = Pedido.objects.exclude(estado='TERMINADO')

    # 3. Clasificación
    criticos = activos.filter(fecha_entrega__lt=hoy).order_by('fecha_entrega')
    urgentes = activos.filter(fecha_entrega__range=[hoy, limite_semana]).order_by('fecha_entrega')
    normales = activos.filter(fecha_entrega__gt=limite_semana).order_by('fecha_entrega')

    # 4. Métricas
    total_activos = activos.count()
    total_presion = criticos.count() + urgentes.count()

    if total_activos > 0:
        nivel_presion = int((total_presion / total_activos) * 100)
    else:
        nivel_presion = 0

    # 5. Métrica Peak Load (CORREGIDA)
    dia_peak_date = None  # Pasamos el objeto fecha, no el texto
    dia_peak_cantidad = 0

    if urgentes.exists():
        fechas = [p.fecha_entrega for p in urgentes]
        # Encontramos la fecha más común
        fecha_mas_comun = max(set(fechas), key=fechas.count)
        dia_peak_cantidad = fechas.count(fecha_mas_comun)
        dia_peak_date = fecha_mas_comun  # Guardamos la fecha real

    context = {
        'criticos': criticos,
        'urgentes': urgentes,
        'normales': normales,
        'nivel_presion': nivel_presion,
        'dia_peak_date': dia_peak_date,  # Nueva variable para el template
        'dia_peak_cantidad': dia_peak_cantidad,
        'hoy': hoy,
    }

    return render(request, 'pedidos/trabajo_semanal.html', context)

# ==========================================
# GESTIÓN DE COTIZACIONES
# ==========================================

@login_required
def lista_cotizaciones(request):
    # 1. Base QuerySet
    cotizaciones = Cotizacion.objects.all().order_by('-created_at')

    # 2. Filtros (Estado)
    estado_filter = request.GET.get('estado')
    if estado_filter:
        cotizaciones = cotizaciones.filter(estado=estado_filter)

    # 3. Búsqueda
    busqueda = request.GET.get('busqueda')
    if busqueda:
        cotizaciones = cotizaciones.filter(
            Q(cliente__nombre__icontains=busqueda) |
            Q(resumen__icontains=busqueda)
        )

    # 4. Paginación
    paginator = Paginator(cotizaciones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cotizaciones': page_obj,
        'page_obj': page_obj,
        'busqueda': busqueda,
        'estado_filter': estado_filter,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'pedidos/cotizacion_list.html', context)


@login_required
@transaccion_segura
def crear_cotizacion(request):
    # Inicializamos ClienteForm por si queremos crear cliente rápido (igual que en Pedidos)
    cliente_form = ClienteForm()
    # NECESARIO: Cargar productos para que el Select2 funcione en el template
    productos_disponibles = Producto.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cotizacion = form.save()

            # --- NUEVA LÓGICA: Guardar Ítems (Espejo de crear_pedido) ---
            items_json = request.POST.get('items_json')
            if items_json:
                try:
                    data_items = json.loads(items_json)
                    for item in data_items:
                        # item es: {'producto_id': '5', 'cantidad': 2, 'precio_unitario': 15000, ...}
                        producto_obj = Producto.objects.get(pk=item['producto_id'])

                        ItemCotizacion.objects.create(
                            cotizacion=cotizacion,
                            producto=producto_obj,
                            cantidad=float(item['cantidad']),
                            precio_unitario=int(item['precio_unitario'])
                        )
                except Exception as e:
                    # En producción podrías loguear esto
                    pass
            # -------------------------------------------------------------

            # Redirigimos al detalle para revisar antes de "enviar"
            return redirect('detalle_cotizacion', pk=cotizacion.pk)
    else:
        form = CotizacionForm(initial={'fecha_emision': timezone.now().date()})

    return render(request, 'pedidos/cotizacion_form.html', {
        'form': form,
        'cliente_form': cliente_form,
        'productos_disponibles': productos_disponibles,
        'fecha_hoy': timezone.now().strftime('%Y-%m-%d')
    })

@login_required
@transaccion_segura
def editar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    productos_disponibles = Producto.objects.all().order_by('nombre')

    if cotizacion.estado == 'ACEPTADA':
        return redirect('detalle_cotizacion', pk=pk)

    if request.method == 'POST':
        form = CotizacionForm(request.POST, instance=cotizacion)
        if form.is_valid():
            cotizacion = form.save()

            items_json = request.POST.get('items_json')
            if items_json:
                try:
                    cotizacion.items.all().delete()
                    data_items = json.loads(items_json)
                    for item in data_items:
                        producto_obj = Producto.objects.get(pk=item['producto_id'])
                        ItemCotizacion.objects.create(
                            cotizacion=cotizacion,
                            producto=producto_obj,
                            cantidad=float(item['cantidad']),
                            precio_unitario=int(item['precio_unitario'])
                        )
                except Exception:
                    pass
            return redirect('detalle_cotizacion', pk=pk)
    else:
        form = CotizacionForm(instance=cotizacion)

    # --- NUEVO: PRE-CARGA DE ÍTEMS ---
    items_list = []
    for item in cotizacion.items.all():
        items_list.append({
            'producto_id': item.producto.id,
            'nombre': item.producto.nombre,
            'unidad': item.producto.get_unidad_display(),
            'cantidad': float(item.cantidad),
            'precio_unitario': item.precio_unitario,
            'subtotal': int(round(item.cantidad * item.precio_unitario))
        })
    # ---------------------------------

    return render(request, 'pedidos/cotizacion_form.html', {
        'form': form,
        'productos_disponibles': productos_disponibles,
        'fecha_hoy': timezone.now().strftime('%Y-%m-%d'),
        'items_json': json.dumps(items_list) # ¡Enviamos los datos!
    })

@login_required
def detalle_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    return render(request, 'pedidos/cotizacion_detail.html', {'cotizacion': cotizacion})


@login_required
@transaccion_segura
def eliminar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    if request.method == 'POST':
        cotizacion.delete()
        return redirect('lista_cotizaciones')
    return render(request, 'pedidos/cotizacion_confirm_delete.html', {'cotizacion': cotizacion})

@login_required
@transaccion_segura
def convertir_a_pedido(request, pk):
    """
    Toma una cotización y crea un Pedido.
    Copia el cliente, datos y AHORA TAMBIÉN LOS PRODUCTOS.
    """
    cotizacion = get_object_or_404(Cotizacion, pk=pk)

    if request.method == 'POST':
        # 1. Capturar datos del formulario de conversión
        fecha_entrega = request.POST.get('fecha_entrega')
        abono = request.POST.get('valor_abonado', 0)

        # 2. Crear el Pedido (Cabecera)
        pedido = Pedido.objects.create(
            cliente=cotizacion.cliente,
            resumen_pedido=cotizacion.resumen,
            detalles_pedido=cotizacion.detalles,
            valor_venta=cotizacion.valor_total,
            valor_abonado=int(abono),
            fecha_entrega=fecha_entrega,
            estado='PENDIENTE',
        )

        # 3. --- NUEVO: TRASPASAR PRODUCTOS (Clonación de Ítems) ---
        # Recorremos los ítems de la cotización y creamos sus gemelos en el pedido
        for item_cot in cotizacion.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_cot.producto,
                cantidad=item_cot.cantidad,
                precio_unitario=item_cot.precio_unitario
            )
        # ------------------------------------------------------------

        # 4. Actualizar la Cotización
        cotizacion.estado = 'ACEPTADA'
        cotizacion.save()

        # 5. Redirigir al nuevo pedido
        return redirect('detalle_pedido', pk=pedido.pk)

    context = {
        'cotizacion': cotizacion,
        'fecha_sugerida': timezone.now().date() + timedelta(days=7)
    }
    return render(request, 'pedidos/cotizacion_convertir.html', context)

@login_required
def exportar_cotizacion_pdf(request, pk):
    # 1. Obtener la cotización
    cotizacion = get_object_or_404(Cotizacion, pk=pk)

    # 2. Renderizar el HTML con los datos
    html_string = render_to_string('pedidos/cotizacion_pdf.html', {
        'cotizacion': cotizacion
    })

    # 3. Crear el objeto HTML de WeasyPrint
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())

    # 4. Generar el PDF
    result = html.write_pdf()

    # 5. Crear la respuesta HTTP con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    # 'inline' para ver en navegador, 'attachment' para descargar directo
    response['Content-Disposition'] = f'inline; filename="Cotizacion_{cotizacion.id}.pdf"'
    response.write(result)

    return response

# ==========================================
# GESTIÓN DE PRODUCTOS (INVENTARIO)
# ==========================================

@login_required
def lista_productos(request):
    # 1. Base QuerySet
    productos = Producto.objects.all().order_by('-fecha_ingreso')

    # 2. Búsqueda
    busqueda = request.GET.get('busqueda')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    # 3. Paginación (10 productos por página)
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'productos': page_obj,
        'page_obj': page_obj,
        'busqueda': busqueda,
        'total_productos': Producto.objects.count(),
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'pedidos/producto_list.html', context)


@login_required
@transaccion_segura
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()

    return render(request, 'pedidos/producto_form.html', {'form': form})


@login_required
@transaccion_segura
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'pedidos/producto_form.html', {'form': form})


@login_required
@transaccion_segura
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    error_message = None # Variable para guardar el mensaje de error

    if request.method == 'POST':
        try:
            producto.delete()
            return redirect('lista_productos')
        except ProtectedError:
            # Aquí capturamos el bloqueo de seguridad
            error_message = "No se puede eliminar este producto porque ya forma parte de Pedidos o Cotizaciones históricas. Para mantener la integridad de los datos, no está permitido borrarlo."

    return render(request, 'pedidos/producto_confirm_delete.html', {
        'producto': producto,
        'error': error_message # Pasamos el error al HTML
    })

@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'pedidos/producto_detail.html', {'producto': producto})

@login_required
@require_POST
def api_crear_producto_rapido(request):
    """
    Endpoint AJAX para crear productos desde el formulario de pedido.
    Recibe 'valor_neto', deja que el modelo calcule el IVA/Bruto,
    y retorna el 'valor_bruto' como precio sugerido.
    """
    form = ProductoForm(request.POST)
    if form.is_valid():
        producto = form.save()  # El modelo calcula iva y valor_bruto aquí

        return JsonResponse({
            'success': True,
            'id': producto.id,
            'nombre': producto.nombre,
            # Devolvemos el valor_bruto para el JS
            'precio': producto.valor_bruto,
            # NUEVO: Devolvemos el nombre legible de la unidad para la tabla (ej: "Metro Cuadrado")
            'unidad': producto.get_unidad_display()
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })

# ==========================================
# BASE DE DATOS - RESPALDOS & RESTAURACIONES
# ==========================================

def es_superusuario(user):
    return user.is_superuser

@login_required
@user_passes_test(es_superusuario)
def respaldar_bd(request):
    """
    Vista Dashboard: Muestra métricas y listado de backups existentes.
    """
    # 1. Recopilar Métricas de la BD actual
    metricas = {
        'total_pedidos': Pedido.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_cotizaciones': Cotizacion.objects.count(),
        'total_productos': Producto.objects.count(),
    }

    # 2. Listar archivos en la carpeta 'backups'
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    lista_backups = []

    if os.path.exists(backup_dir):
        with os.scandir(backup_dir) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('.sql') and entry.name != '.gitkeep':
                    # Obtener stats del archivo
                    stats = entry.stat()
                    fecha_mod = datetime.fromtimestamp(stats.st_mtime)

                    lista_backups.append({
                        'nombre': entry.name,
                        'fecha': fecha_mod,
                        'size_mb': round(stats.st_size / (1024 * 1024), 2) # Peso en MB
                    })

    # 3. Ordenar: El más reciente primero
    lista_backups.sort(key=lambda x: x['fecha'], reverse=True)

    return render(request, 'pedidos/respaldar_bd.html', {
        'metricas': metricas,
        'backups': lista_backups
    })

@login_required
@user_passes_test(es_superusuario)
def generar_respaldo_bd(request):
    """
    Acción: Genera el .sql y fuerza la descarga.
    """
    try:
        ruta_archivo = generar_respaldo_mysql()
        archivo = open(ruta_archivo, 'rb')
        response = FileResponse(archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response
    except Exception as e:
        return HttpResponse(f"Error crítico: {str(e)}")

@login_required
@user_passes_test(es_superusuario)
def restaurar_bd(request):
    """
    Vista delicada:
    1. GET: Muestra el formulario de advertencia y carga.
    2. POST: Recibe el archivo, hace un respaldo de emergencia y restaura la BD.
    """
    if request.method == 'POST':
        # 1. Validar que se envió un archivo
        if 'archivo_sql' not in request.FILES:
            messages.error(request, "No se seleccionó ningún archivo.")
            return redirect('restaurar_bd')

        archivo = request.FILES['archivo_sql']

        # 2. Validar extensión
        if not archivo.name.endswith('.sql'):
            messages.error(request, "Error: El archivo debe tener extensión .sql")
            return redirect('restaurar_bd')

        try:
            # 3. Guardar el archivo temporalmente en 'backups/tmp/'
            # (Usamos FileSystemStorage para manejar la subida de forma segura)
            ruta_tmp = os.path.join(settings.BASE_DIR, 'backups', 'tmp')
            if not os.path.exists(ruta_tmp):
                os.makedirs(ruta_tmp)

            fs = FileSystemStorage(location=ruta_tmp)
            nombre_archivo = fs.save(archivo.name, archivo)
            ruta_absoluta = fs.path(nombre_archivo)

            # ====================================================
            # EL AIRBAG: Respaldo de Emergencia Automático
            # ====================================================
            try:
                generar_respaldo_mysql()  # Si esto falla, NO restauramos
            except Exception as e:
                # Si no podemos hacer el respaldo de seguridad, ABORTAMOS la misión.
                # Es mejor no restaurar que restaurar sin red de seguridad.
                if os.path.exists(ruta_absoluta): os.remove(ruta_absoluta)  # Limpieza
                messages.error(request,
                               f"Operación abortada: No se pudo crear el respaldo de seguridad previo ({str(e)}).")
                return redirect('restaurar_bd')

            # ====================================================
            # LA RESTAURACIÓN: El momento de la verdad
            # ====================================================
            restaurar_bd_mysql(ruta_absoluta)

            # Si llegamos aquí, es porque salió bien
            messages.success(request, f"¡Éxito! La base de datos fue restaurada con el archivo: {archivo.name}")

            # Limpieza: Borrar el archivo que subimos para restaurar
            if os.path.exists(ruta_absoluta):
                os.remove(ruta_absoluta)

        except Exception as e:
            messages.error(request, f"Error crítico al restaurar: {str(e)}")

        return redirect('restaurar_bd')

    # Si es GET, solo mostramos el formulario
    return render(request, 'pedidos/restaurar_bd.html')

# ==========================================
# GESTIÓN DE ERRORES HTTP
# ==========================================

def error_404(request, exception):
    return render(request, 'pedidos/errors/404.html', status=404)

def error_500(request):
    return render(request, 'pedidos/errors/500.html', status=500)
