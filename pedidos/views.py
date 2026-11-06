from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, login_not_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Count, Sum, F, ProtectedError, F, Value, IntegerField
from django.db.models.functions import TruncMonth, Coalesce
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST, require_safe
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import transaction
from .models import Pedido, Cliente, Cotizacion, Producto, ItemPedido, ItemCotizacion, HistorialBD, Pago
from .forms import PedidoForm, ClienteForm, CotizacionForm, ProductoForm, PagoForm, ConversionCotizacionForm
from .eventos import registrar_evento
from . import envio_unico
from .utils import generar_respaldo_mysql, restaurar_bd_mysql, registrar_metricas_diarias
from datetime import timedelta, datetime
from PedidosApp import settings
import json
import logging
from decimal import Decimal, InvalidOperation
import os

logger = logging.getLogger(__name__)

# Fallos de un ítem que el servidor devuelve al formulario en vez de la página 500 (03-04, decisión 3-B).
# Son las cinco causas medidas en las pruebas: producto inexistente, JSON inválido, clave ausente y
# cantidad o precio no numéricos. Cualquier otra excepción sigue yendo a la página 500 (RDA-019).
ERRORES_DE_ITEM = (json.JSONDecodeError, KeyError, TypeError, ValueError, Producto.DoesNotExist)

# Textos aprobados por el desarrollador el 2026-11-04.
TEXTO_ITEM_FALLIDO = ('No pudimos guardar el detalle de productos. Lo que escribiste sigue en pantalla: '
                      'revísalo y vuelve a guardar. Si el problema sigue, avisa en qué pantalla estabas y a qué hora.')
TEXTO_IMAGEN = 'Vuelve a elegir la imagen de referencia: el navegador no la conserva.'
TEXTO_FORMULARIO_VENCIDO = 'Este formulario venció y no se guardó. Revisa los datos y vuelve a guardar.'


def _avisar_formulario_vencido(request):
    """Un envío sin token válido no crea nada: se deja una línea INFO (sin el contenido) y se avisa al usuario."""
    logger.info('Envío sin token válido; no se guardó nada', extra={'request': request})
    messages.error(request, TEXTO_FORMULARIO_VENCIDO)


def _abono_devuelto(request):
    """El abono que escribió el usuario, para devolverlo al formulario de creación (03-04).

    Solo si es un número mayor que 0, la misma condición con que `index.js` habilita el método de pago:
    un `<select>` deshabilitado no se envía y el pedido se guardaría sin su pago inicial.
    """
    crudo = request.POST.get('abono_inicial', '').strip()
    try:
        abono = Decimal(crudo)
    except InvalidOperation:
        return ''
    return crudo if abono.is_finite() and abono > 0 else ''


def _avisar_si_se_pierde_la_imagen(request):
    """El navegador no vuelve a rellenar un campo de archivo: si traía una imagen, se avisa."""
    if 'imagen_referencia' in request.FILES:
        messages.error(request, TEXTO_IMAGEN)


# ==========================================
# PANEL DE CONTROL
# ==========================================
@login_required
def dashboard(request):
    # ==========================================
    # 0. GATILLO DE ESTADÍSTICAS
    # ==========================================
    registrar_metricas_diarias()

    ahora = timezone.now()
    hoy = ahora.date()

    # ==========================================
    # 1. TARJETA 1 (VERDE): ÚLTIMO RESPALDO BD (Lectura de archivos, no BD)
    # ==========================================
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    ultimo_respaldo_fecha = None

    if os.path.exists(backup_dir):
        archivos = [
            os.path.join(backup_dir, f)
            for f in os.listdir(backup_dir)
            if f.endswith('.sql')
        ]
        if archivos:
            mas_reciente = max(archivos, key=os.path.getmtime)
            ultimo_respaldo_fecha = datetime.fromtimestamp(os.path.getmtime(mas_reciente))

    # =========================================================================
    # OPTIMIZACIÓN: 1 SOLA CONSULTA PARA TODAS LAS TARJETAS Y EL GRÁFICO
    # =========================================================================
    limite_semana = hoy + timedelta(days=7)
    inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Convertimos 7 viajes a la base de datos en 1 solo usando aggregate y Q objects
    conteos = Pedido.objects.aggregate(
        # Tarjeta 2: Críticos (Atrasados y no terminados)
        criticos=Count('id', filter=~Q(estado='TERMINADO') & Q(fecha_entrega__lt=hoy)),

        # Tarjeta 3: Urgentes (Próximos 7 días y no terminados)
        urgentes=Count('id', filter=~Q(estado='TERMINADO') & Q(fecha_entrega__range=[hoy, limite_semana])),

        # Tarjeta 4 y Total Dona: Mes Actual
        mes_actual=Count('id', filter=Q(fecha_solicitud__gte=inicio_mes_actual)),

        # Dona: Pendientes del mes
        mes_pendientes=Count('id', filter=Q(fecha_solicitud__gte=inicio_mes_actual) & Q(estado='PENDIENTE')),

        # Dona: En proceso del mes
        mes_en_proceso=Count('id', filter=Q(fecha_solicitud__gte=inicio_mes_actual) & Q(estado='EN_PROCESO')),

        # Dona: Completados del mes
        mes_completados=Count('id', filter=Q(fecha_solicitud__gte=inicio_mes_actual) & Q(estado='TERMINADO'))
    )

    # Asignación de variables con fallback a 0
    criticos_count = conteos['criticos'] or 0
    urgentes_count = conteos['urgentes'] or 0
    pedidos_mes_count = conteos['mes_actual'] or 0

    total_pedidos = conteos['mes_actual'] or 0
    pendientes = conteos['mes_pendientes'] or 0
    en_proceso = conteos['mes_en_proceso'] or 0
    completados = conteos['mes_completados'] or 0

    # Cálculo de Porcentajes (Conic Gradient CSS)
    if total_pedidos > 0:
        pct_pendientes = (pendientes / total_pedidos) * 100
        pct_en_proceso = (en_proceso / total_pedidos) * 100
        stop_1 = pct_pendientes
        stop_2 = pct_pendientes + pct_en_proceso
    else:
        stop_1 = 0
        stop_2 = 0

    pct_text_pendientes = round((pendientes / total_pedidos * 100)) if total_pedidos > 0 else 0
    pct_text_proceso = round((en_proceso / total_pedidos * 100)) if total_pedidos > 0 else 0
    pct_text_completados = round((completados / total_pedidos * 100)) if total_pedidos > 0 else 0

    # ==========================================
    # B. Datos para Gráfico de Barras (Top Clientes Histórico)
    # ==========================================
    top_clientes = Cliente.objects.annotate(
        num_pedidos=Count('pedido')
    ).order_by('-num_pedidos')[:5]

    max_pedidos = top_clientes[0].num_pedidos if top_clientes else 1

    # ==========================================
    # 3. CONTEXTO
    # ==========================================
    context = {
        'ultimo_respaldo_fecha': ultimo_respaldo_fecha,
        'criticos_count': criticos_count,
        'urgentes_count': urgentes_count,
        'pedidos_mes_count': pedidos_mes_count,
        'fecha_actual': ahora,
        'total_pedidos': total_pedidos,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'completados': completados,
        'donut_stop_1': stop_1,
        'donut_stop_2': stop_2,
        'pct_pendientes': pct_text_pendientes,
        'pct_proceso': pct_text_proceso,
        'pct_completados': pct_text_completados,
        'top_clientes': top_clientes,
        'max_pedidos': max_pedidos,
    }

    return render(request, 'pedidos/dashboard.html', context)

# ==========================================
# FUNCIÓN AUXILIAR - Para determinar estado de pago
# ==========================================
def actualizar_estado_pago_pedido(pedido):
    """Recalcula y guarda el estado financiero del pedido basado en sus pagos.

    Se llama dentro del mismo `transaction.atomic` que escribe el pago o el valor de venta
    (03-03, AUD-02-004). Guarda solo `estado_pago`, para no pisar otros campos con valores viejos.
    """
    if pedido.saldo_pendiente <= 0:
        pedido.estado_pago = 'PAGADO'
    elif pedido.total_pagado_real > 0:
        pedido.estado_pago = 'PARCIAL'
    else:
        pedido.estado_pago = 'PENDIENTE'
    pedido.save(update_fields=['estado_pago'])

# ==========================================
# GESTIÓN DE PEDIDOS
# ==========================================

@login_required
def crear_pedido(request):
    cliente_form = ClienteForm()
    productos_disponibles = Producto.objects.all().order_by('nombre')
    clientes = Cliente.objects.all()
    estado_envio, token = None, None

    if request.method == 'POST':
        # Envío único (03-04, AUD-04-001): un envío repetido termina en el pedido ya creado.
        estado_envio, token, ya_creado = envio_unico.estado(request, 'pedido')
        if estado_envio == envio_unico.USADO:
            return redirect('detalle_pedido', pk=ya_creado)

        form = PedidoForm(request.POST, request.FILES)

        if estado_envio == envio_unico.INVALIDO:
            _avisar_formulario_vencido(request)
        elif form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar el Pedido (Padre) - REGLA DE ORO: Legacy en 0
                    pedido = form.save(commit=False)
                    pedido.creado_por = request.user

                    # Calculamos el estado de pago inicial (PENDIENTE por defecto)
                    # Como el abono va a la tabla Pago, el pedido nace "debiendo el 100%" técnicamente
                    # hasta que consultemos la tabla Pago, pero por ahora lo dejamos limpio.
                    pedido.estado_pago = 'PENDIENTE'

                    pedido.save()

                    # 2. Procesar los Ítems (Hijos)
                    # Si un ítem falla, la excepción sale del bloque atomic: se revierte todo (pedido, ítems
                    # y pago) (03-02, RDA-019). Las causas conocidas las atiende el except de más abajo
                    # (03-04); cualquier otra excepción responde 500 con la traza en server.log.
                    items_json = request.POST.get('items_json')
                    if items_json:
                        data_items = json.loads(items_json)
                        for item in data_items:
                            producto_obj = Producto.objects.get(pk=item['producto_id'])
                            ItemPedido.objects.create(
                                pedido=pedido,
                                producto=producto_obj,
                                cantidad=float(item['cantidad']),
                                precio_unitario=int(item['precio_unitario'])
                            )

                    # 3. Lógica de Pago (CORREGIDA: Variable segura y flujo directo)
                    # Extraemos el valor del formulario de manera segura
                    abono_inicial = form.cleaned_data.get('abono_inicial')

                    # Si el usuario ingresó un monto, creamos el registro en la tabla Pago
                    if abono_inicial and abono_inicial > 0:
                        # Capturar el metodo desde el HTML
                        metodo_seleccionado = request.POST.get('metodo_pago', 'EFECTIVO')

                        # Crear el registro de Pago (Aquí vive el dato real)
                        Pago.objects.create(
                            pedido=pedido,
                            monto=abono_inicial,
                            metodo=metodo_seleccionado,
                            fecha=timezone.now(),
                            registrado_por=request.user,
                            nota='Abono inicial al crear pedido'
                        )

                        # El estado financiero sigue al pago, dentro de la misma transacción (03-03, R10).
                        actualizar_estado_pago_pedido(pedido)

                        # OJO: NO actualizamos pedido.valor_abonado.
                        # Se mantiene en 0 como solicitaste.

                    # Evento de auditoría (01-04): se escribe cuando la transacción se confirma.
                    con_abono = ' con abono inicial' if abono_inicial and abono_inicial > 0 else ''
                    registrar_evento('pedido_creado', request.user, 'pedido', pedido.pk,
                                     f'Pedido #{pedido.pk} creado{con_abono}')

                envio_unico.consumir(request, token, pedido.pk)
                return redirect('detalle_pedido', pk=pedido.pk)
            except ERRORES_DE_ITEM:
                # Un ítem no se pudo guardar: el atomic ya revirtió todo. Se registra con la traza y se
                # devuelve el formulario con lo que escribió el usuario (03-04, decisiones 3-B y 4-A).
                logger.exception('Un ítem del pedido no se pudo guardar', extra={'request': request})
                messages.error(request, TEXTO_ITEM_FALLIDO)
                # El guardado llegó a asignar un pk al objeto en memoria: se vuelve a armar el formulario.
                form = PedidoForm(request.POST)

        else:
            # Solo los nombres de los campos: los mensajes pueden repetir lo que escribió el usuario.
            logger.info('Formulario de pedido inválido; campos con error: %s',
                        ', '.join(sorted(form.errors)), extra={'request': request})

        _avisar_si_se_pierde_la_imagen(request)
    else:
        form = PedidoForm()

    context = {
        'form': form,
        'cliente_form': cliente_form,
        'productos_disponibles': productos_disponibles,
        'clientes': clientes,
        'productos': productos_disponibles,
        # Lo que el usuario ya armó (03-04, decisión 4-A): los ítems y el método del abono.
        'items_json': request.POST.get('items_json', ''),
        'metodo_pago': request.POST.get('metodo_pago', ''),
        'abono_devuelto': _abono_devuelto(request),
        # El token que ya trajo el envío sigue valiendo mientras no se guarde; si no, uno nuevo.
        'token_envio': token if estado_envio == envio_unico.NUEVO else envio_unico.emitir(request, 'pedido'),
    }

    return render(request, 'pedidos/pedido_form.html', context)

@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    productos_disponibles = Producto.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            # El pedido, el borrado y la recreación de ítems y el estado financiero son una sola
            # unidad (03-03, RDA-019). Si algo falla, la excepción sale del bloque atomic: quedan los
            # ítems y el valor anteriores y no se escribe el evento. Las causas conocidas de un ítem
            # fallido las atiende el except (03-04); cualquier otra responde 500 con la traza.
            try:
                with transaction.atomic():
                    pedido = form.save()

                    items_json = request.POST.get('items_json')
                    if items_json:
                        pedido.items.all().delete()  # Borrón
                        data_items = json.loads(items_json)
                        for item in data_items:
                            producto_obj = Producto.objects.get(pk=item['producto_id'])
                            ItemPedido.objects.create(
                                pedido=pedido,
                                producto=producto_obj,
                                cantidad=float(item['cantidad']),
                                precio_unitario=int(item['precio_unitario'])
                            )

                    # El valor de venta pudo cambiar (R11).
                    actualizar_estado_pago_pedido(pedido)
                    registrar_evento('pedido_modificado', request.user, 'pedido', pedido.pk,
                                     f'Pedido #{pedido.pk} modificado')
                # Redirigir al detalle del pedido editado
                return redirect('detalle_pedido', pk=pedido.pk)
            except ERRORES_DE_ITEM:
                # Un ítem no se pudo guardar: el atomic ya revirtió todo y la base conserva los ítems y el
                # valor anteriores. Se devuelve el formulario con lo que escribió el usuario (03-04, 3-B y 4-A).
                logger.exception('Un ítem del pedido no se pudo guardar al editar', extra={'request': request})
                messages.error(request, TEXTO_ITEM_FALLIDO)
        _avisar_si_se_pierde_la_imagen(request)
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

    # Si el formulario vuelve con un error, van los ítems que el usuario envió y no los de la base
    # (03-04, decisión 4-A). Sin ítems en el envío, quedan los de la base.
    items_json = request.POST.get('items_json') or json.dumps(items_list)

    return render(request, 'pedidos/pedido_form.html', {
        'form': form,
        'productos_disponibles': productos_disponibles,
        'items_json': items_json  # ¡Aquí enviamos los datos al HTML!
    })

@login_required
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        registrar_evento('pedido_eliminado', request.user, 'pedido', pk, f'Pedido #{pk} eliminado')
        return redirect('lista_pedidos')
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
        estado_anterior = pedido.estado
        pedido.estado = nuevo_estado
        pedido.save()
        if estado_anterior != nuevo_estado:
            registrar_evento('pedido_estado_cambiado', request.user, 'pedido', pedido.pk,
                             f'Pedido #{pedido.pk}: {estado_anterior} -> {nuevo_estado}')

    return redirect('detalle_pedido', pk=pk)

@login_required
def lista_pedidos(request):
    # =========================================================================
    # OPTIMIZACIÓN 1: Unificar las 4 consultas de conteo en 1 sola (aggregate)
    # =========================================================================
    conteos = Pedido.objects.aggregate(
        total=Count('id'),
        pendientes=Count('id', filter=Q(estado='PENDIENTE')),
        en_proceso=Count('id', filter=Q(estado='EN_PROCESO')),
        completados=Count('id', filter=Q(estado='TERMINADO'))
    )

    total_pedidos = conteos['total'] or 0
    pendientes = conteos['pendientes'] or 0
    en_proceso = conteos['en_proceso'] or 0
    completados = conteos['completados'] or 0

    # =========================================================================
    # OPTIMIZACIÓN 2: Prevenir N+1 usando select_related('cliente')
    # =========================================================================
    # Base QuerySet: Trae los pedidos Y los clientes asociados en un solo viaje.
    pedidos = Pedido.objects.select_related('cliente').all()

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
def duplicar_pedido(request, pk):
    # 1. Obtener el pedido original
    original = get_object_or_404(Pedido, pk=pk)

    # 2. Crear una copia en memoria (sin PK para que sea nuevo)
    nuevo_pedido = Pedido(
        cliente=original.cliente,
        resumen_pedido=original.resumen_pedido,
        detalles_pedido=original.detalles_pedido,
        valor_venta=original.valor_venta,
        estado='PENDIENTE',  # IMPORTANTE: Nace pendiente
        fecha_entrega=original.fecha_entrega,  # Mantenemos fecha ref, usuario editará si quiere
        imagen_referencia=original.imagen_referencia  # Mantenemos la imagen si tenía
    )

    # 3. Guardar el nuevo registro (esto genera fecha_solicitud actual automática)
    nuevo_pedido.save()
    registrar_evento('pedido_duplicado', request.user, 'pedido', nuevo_pedido.pk,
                     f'Pedido #{nuevo_pedido.pk} duplicado desde el pedido #{original.pk}')

    # 4. Redirigir al detalle del nuevo pedido clonado
    return redirect('detalle_pedido', pk=nuevo_pedido.pk)

@login_required
def estadisticas_pedidos(request):
    """
    Vista de Analítica de Ventas y Pedidos.
    FASE 1 COMPLETADA: Fechas + Queries + Gráfico SVG.
    """
    # 1. Definir el "Ahora"
    hoy = timezone.now()

    # ---------------------------------------------------------
    # A. DEFINICIÓN DE RANGOS TEMPORALES
    # ---------------------------------------------------------
    inicio_mes_actual = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
    inicio_mes_anterior = fin_mes_anterior.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fecha_corte_anual = (inicio_mes_actual - timedelta(days=365)).replace(day=1)

    # ---------------------------------------------------------
    # B. CONSULTAS (KPIs)
    # ---------------------------------------------------------

    # KPI 1: TOTAL PEDIDOS MES ACTUAL
    pedidos_mes_actual = Pedido.objects.filter(fecha_solicitud__gte=inicio_mes_actual)
    total_mes_actual = pedidos_mes_actual.count()

    # KPI 2: CRECIMIENTO VS MES ANTERIOR
    pedidos_mes_anterior = Pedido.objects.filter(
        fecha_solicitud__range=[inicio_mes_anterior, fin_mes_anterior]
    ).count()

    if pedidos_mes_anterior > 0:
        crecimiento_pct = ((total_mes_actual - pedidos_mes_anterior) / pedidos_mes_anterior) * 100
    else:
        crecimiento_pct = 100 if total_mes_actual > 0 else 0

    # KPI 3: TASA DE EFICIENCIA (COMPLETADOS VS TOTALES DEL MES)
    # Cuántos de los pedidos de ESTE mes ya están terminados
    completados_mes = pedidos_mes_actual.filter(estado='TERMINADO').count()

    if total_mes_actual > 0:
        eficiencia_pct = (completados_mes / total_mes_actual) * 100
    else:
        eficiencia_pct = 0
    # ---------------------------------------------------------
    # C. DATOS PARA EL GRÁFICO (Enero a Diciembre del Año Actual)
    # ---------------------------------------------------------
    year_actual = str(hoy.year)

    # 1. Crear una plantilla de 12 meses en cero
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    datos_anuales = [{'mes_idx': i, 'label': meses_nombres[i - 1], 'total': 0} for i in range(1, 13)]

    # 2. Consultar la BD solo para los pedidos del año actual
    datos_bd = (
        Pedido.objects
        .filter(fecha_solicitud__year=hoy.year)  # Usamos hoy.year en vez del string
        .annotate(mes=TruncMonth('fecha_solicitud'))
        .values('mes')
        .annotate(total=Count('id'))
    )

    # 3. Fusionar datos reales con nuestra plantilla de 12 meses
    for d in datos_bd:
        mes_db = d['mes'].month  # Retorna de 1 a 12
        datos_anuales[mes_db - 1]['total'] = d['total']

    # ---------------------------------------------------------
    # D. LÓGICA SVG (GEOMETRÍA - Corregida)
    # ---------------------------------------------------------
    puntos_svg = ""
    area_svg = ""
    lista_puntos = []

    # 1. Escala Vertical (Eje Y)
    valores = [d['total'] for d in datos_anuales]
    max_val = max(valores)
    max_y = max_val * 1.2 if max_val > 0 else 10  # 20% de aire arriba

    # 2. Configuración Canvas SVG (1000x400)
    canvas_height = 400
    canvas_width = 1000
    padding_top = 50
    padding_bottom = 50
    util_height = canvas_height - padding_top - padding_bottom

    # 3. Calcular Coordenadas exactas para los 12 meses
    cantidad_puntos = 12
    step_x = canvas_width / (cantidad_puntos - 1)
    coords = []

    for i, dato in enumerate(datos_anuales):
        cx = int(i * step_x)
        valor = float(dato['total'])
        cy = int((canvas_height - padding_bottom) - ((valor / max_y) * util_height))

        coords.append(f"{cx},{cy}")

        lista_puntos.append({
            'x': str(cx),
            'y': str(cy),
            'label': dato['label'],
            'valor': int(valor),
        })

    # 4. Construir Path SVG
    puntos_svg = "M " + " L ".join(coords)
    area_svg = f"{puntos_svg} V {canvas_height} H 0 Z"

    context = {
        # ... (Mantienes tus KPIs existentes aquí) ...
        'total_mes_actual': total_mes_actual,
        'crecimiento_pct': round(crecimiento_pct, 1),
        'eficiencia_pct': round(eficiencia_pct, 1),

        # Nuevas variables del Gráfico Anual
        'year_actual': year_actual,
        'puntos_svg': puntos_svg,
        'area_svg': area_svg,
        'lista_puntos': lista_puntos,
        'max_y_label': int(max_y),
        'mitad_y_label': int(max_y / 2)
    }

    return render(request, 'pedidos/estadisticas_pedidos.html', context)

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
        'clientes_nuevos': 0,  # Placeholder
        'top_cliente': top_cliente,
        'busqueda': busqueda,
    }
    return render(request, 'pedidos/cliente_list.html', context)

@login_required
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
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        registrar_evento('cliente_eliminado', request.user, 'cliente', pk, f'Cliente #{pk} eliminado')
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

    # =========================================================================
    # OPTIMIZACIÓN 1: Prevenir N+1 (select_related)
    # =========================================================================
    # Al pedir activos, forzamos un INNER JOIN con 'cliente' desde el principio.
    # Así, cuando el HTML pida {{ pedido.cliente.nombre }}, el dato ya estará en memoria.
    activos = Pedido.objects.select_related('cliente').exclude(estado='TERMINADO')

    # 3. Clasificación
    criticos = activos.filter(fecha_entrega__lt=hoy).order_by('fecha_entrega')
    urgentes = activos.filter(fecha_entrega__range=[hoy, limite_semana]).order_by('fecha_entrega')
    normales = activos.filter(fecha_entrega__gt=limite_semana).order_by('fecha_entrega')

    # 4. Métricas
    # Usamos len() en lugar de .count() porque vamos a iterar sobre estos querysets
    # en el HTML sí o sí. Al usar len(), Django evalúa la consulta 1 sola vez,
    # ahorrando 3 viajes adicionales "SELECT COUNT" a la BD.
    total_criticos = len(criticos)
    total_urgentes = len(urgentes)
    total_activos = len(activos)

    total_presion = total_criticos + total_urgentes

    if total_activos > 0:
        nivel_presion = int((total_presion / total_activos) * 100)
    else:
        nivel_presion = 0

    # =========================================================================
    # OPTIMIZACIÓN 2: Procesamiento SQL (Día Peak)
    # =========================================================================
    # Le decimos a MySQL: "Toma los urgentes, agrúpalos por fecha, cuenta cuántos
    # hay en cada grupo, ordénalos de mayor a menor, y dame solo el ganador".
    peak_data = urgentes.values('fecha_entrega').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad', 'fecha_entrega').first()

    if peak_data:
        dia_peak_date = peak_data['fecha_entrega']
        dia_peak_cantidad = peak_data['cantidad']
    else:
        dia_peak_date = None
        dia_peak_cantidad = 0

    context = {
        'criticos': criticos,
        'urgentes': urgentes,
        'normales': normales,
        'nivel_presion': nivel_presion,
        'dia_peak_date': dia_peak_date,
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
def crear_cotizacion(request):
    # Inicializamos ClienteForm por si queremos crear cliente rápido (igual que en Pedidos)
    cliente_form = ClienteForm()
    # NECESARIO: Cargar productos para que el Select2 funcione en el template
    productos_disponibles = Producto.objects.all().order_by('nombre')

    estado_envio, token = None, None

    if request.method == 'POST':
        # Envío único (03-04, AUD-04-001): un envío repetido termina en la cotización ya creada.
        estado_envio, token, ya_creada = envio_unico.estado(request, 'cotizacion')
        if estado_envio == envio_unico.USADO:
            return redirect('detalle_cotizacion', pk=ya_creada)

        form = CotizacionForm(request.POST)
        if estado_envio == envio_unico.INVALIDO:
            _avisar_formulario_vencido(request)
        elif form.is_valid():
            # La cotización y sus ítems son una sola unidad (03-03, RDA-019). Si un ítem falla, la
            # excepción sale del bloque atomic y se revierte todo. Las causas conocidas las atiende el
            # except (03-04); cualquier otra responde 500 con la traza en server.log.
            try:
                with transaction.atomic():
                    cotizacion = form.save()

                    # --- Guardar Ítems (Espejo de crear_pedido) ---
                    items_json = request.POST.get('items_json')
                    if items_json:
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
                    # -----------------------------------------------

                # Redirigimos al detalle para revisar antes de "enviar"
                envio_unico.consumir(request, token, cotizacion.pk)
                return redirect('detalle_cotizacion', pk=cotizacion.pk)
            except ERRORES_DE_ITEM:
                # Un ítem no se pudo guardar: el atomic ya revirtió todo (03-04, decisiones 3-B y 4-A).
                logger.exception('Un ítem de la cotización no se pudo guardar', extra={'request': request})
                messages.error(request, TEXTO_ITEM_FALLIDO)
                # El guardado llegó a asignar un pk al objeto en memoria: se vuelve a armar el formulario.
                form = CotizacionForm(request.POST)
    else:
        form = CotizacionForm(initial={'fecha_emision': timezone.now().date()})

    return render(request, 'pedidos/cotizacion_form.html', {
        'form': form,
        'cliente_form': cliente_form,
        'productos_disponibles': productos_disponibles,
        'fecha_hoy': timezone.now().strftime('%Y-%m-%d'),
        # Lo que el usuario ya armó, si el formulario vuelve con un error (03-04, decisión 4-A).
        'items_json': request.POST.get('items_json', ''),
        'token_envio': token if estado_envio == envio_unico.NUEVO else envio_unico.emitir(request, 'cotizacion'),
    })

@login_required
def editar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    productos_disponibles = Producto.objects.all().order_by('nombre')

    if cotizacion.estado == 'ACEPTADA':
        return redirect('detalle_cotizacion', pk=pk)

    if request.method == 'POST':
        form = CotizacionForm(request.POST, instance=cotizacion)
        if form.is_valid():
            # Borrar y recrear los ítems va junto con el guardado de la cotización (03-03, RDA-019):
            # si algo falla, la excepción sale del bloque y quedan los ítems y el valor anteriores.
            try:
                with transaction.atomic():
                    cotizacion = form.save()

                    items_json = request.POST.get('items_json')
                    if items_json:
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
                return redirect('detalle_cotizacion', pk=pk)
            except ERRORES_DE_ITEM:
                # Un ítem no se pudo guardar: el atomic ya revirtió todo y la base conserva los ítems y el
                # valor anteriores. Se devuelve el formulario con lo que escribió el usuario (03-04, 3-B y 4-A).
                logger.exception('Un ítem de la cotización no se pudo guardar al editar',
                                 extra={'request': request})
                messages.error(request, TEXTO_ITEM_FALLIDO)
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

    # Si el formulario vuelve con un error, van los ítems que el usuario envió y no los de la base
    # (03-04, decisión 4-A). Sin ítems en el envío, quedan los de la base.
    items_json = request.POST.get('items_json') or json.dumps(items_list)

    return render(request, 'pedidos/cotizacion_form.html', {
        'form': form,
        'productos_disponibles': productos_disponibles,
        'fecha_hoy': timezone.now().strftime('%Y-%m-%d'),
        'items_json': items_json  # ¡Enviamos los datos!
    })

@login_required
def detalle_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    return render(request, 'pedidos/cotizacion_detail.html', {'cotizacion': cotizacion})

@login_required
def eliminar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    if request.method == 'POST':
        cotizacion.delete()
        return redirect('lista_cotizaciones')
    return render(request, 'pedidos/cotizacion_confirm_delete.html', {'cotizacion': cotizacion})

@login_required
def convertir_a_pedido(request, pk):
    """
    Toma una cotización y crea un Pedido.
    Copia el cliente, datos, productos y GENERA EL PAGO INICIAL SI EXISTE.

    Todo va en una sola transacción (03-03, AUD-02-005, RDA-019): el pedido, sus ítems, el pago,
    el estado financiero y el cierre de la cotización se confirman juntos o no queda nada. La
    cotización se bloquea mientras se convierte, y una ya aceptada vuelve a su detalle sin crear
    nada (la pantalla de detalle ya la muestra como ACEPTADA).
    """
    cotizacion = get_object_or_404(Cotizacion, pk=pk)

    if request.method == 'POST':
        with transaction.atomic():
            cotizacion = get_object_or_404(Cotizacion.objects.select_for_update(), pk=pk)
            if cotizacion.estado == 'ACEPTADA':
                return redirect('detalle_cotizacion', pk=pk)

            # 1. Validar los datos del formulario (fecha y abono)
            form = ConversionCotizacionForm(request.POST, valor_total=cotizacion.valor_total)
            if form.is_valid():
                abono = form.cleaned_data['valor_abonado']

                # 2. Crear el Pedido (Cabecera)
                # IMPORTANTE: Inicializamos valor_abonado en 0. Si hay abono, lo sumará la lógica de Pago.
                pedido = Pedido.objects.create(
                    cliente=cotizacion.cliente,
                    resumen_pedido=cotizacion.resumen,
                    detalles_pedido=cotizacion.detalles,
                    valor_venta=cotizacion.valor_total,
                    fecha_entrega=form.cleaned_data['fecha_entrega'],
                    estado='PENDIENTE',
                    creado_por=request.user
                )

                # 3. Traspasar Productos
                for item_cot in cotizacion.items.all():
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item_cot.producto,
                        cantidad=item_cot.cantidad,
                        precio_unitario=item_cot.precio_unitario
                    )

                # 4. --- LÓGICA DE PAGO INICIAL ---
                if abono > 0:
                    metodo = request.POST.get('metodo_pago', 'TRANSFERENCIA')
                    Pago.objects.create(
                        pedido=pedido,
                        monto=abono,
                        metodo=metodo,
                        fecha=timezone.now(),
                        registrado_por=request.user,
                        nota=f'Abono inicial por conversión de Cotización #{cotizacion.id}'
                    )

                    # Calcular estado financiero
                    actualizar_estado_pago_pedido(pedido)
                # ---------------------------------------------

                # 5. Cerrar la Cotización
                cotizacion.estado = 'ACEPTADA'
                cotizacion.save()
                registrar_evento('cotizacion_convertida', request.user, 'cotizacion', cotizacion.pk,
                                 f'Cotización #{cotizacion.pk} convertida en el pedido #{pedido.pk}')

                # 6. Redirigir al nuevo pedido
                messages.success(request, f"Cotización convertida exitosamente en el Pedido #{pedido.id}")
                return redirect('detalle_pedido', pk=pedido.pk)
        # Datos inválidos: no se escribió nada; la página vuelve con los errores y lo escrito.
    else:
        if cotizacion.estado == 'ACEPTADA':
            return redirect('detalle_cotizacion', pk=pk)
        form = ConversionCotizacionForm(valor_total=cotizacion.valor_total)

    context = {
        'cotizacion': cotizacion,
        'form': form,
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

    # 3. Crear el objeto HTML de WeasyPrint.
    # Se importa aquí y no en la cabecera: WeasyPrint es pesado y solo lo usa esta vista.
    # Con un único worker que hiberna, importarlo al arrancar alarga cada arranque en frío.
    # Si su importación falla, el error aparece al exportar el PDF y no impide iniciar la app.
    import weasyprint

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
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    error_message = None  # Variable para guardar el mensaje de error

    if request.method == 'POST':
        try:
            producto.delete()
            registrar_evento('producto_eliminado', request.user, 'producto', pk, f'Producto #{pk} eliminado')
            return redirect('lista_productos')
        except ProtectedError:
            # Aquí capturamos el bloqueo de seguridad
            error_message = "No se puede eliminar este producto porque ya forma parte de Pedidos o Cotizaciones históricas. Para mantener la integridad de los datos, no está permitido borrarlo."

    return render(request, 'pedidos/producto_confirm_delete.html', {
        'producto': producto,
        'error': error_message  # Pasamos el error al HTML
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
                        'size_mb': round(stats.st_size / (1024 * 1024), 2)  # Peso en MB
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
        registrar_evento('respaldo_generado', request.user, 'respaldo', None,
                         f'Respaldo {os.path.basename(ruta_archivo)} generado')
        archivo = open(ruta_archivo, 'rb')
        response = FileResponse(archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response
    except Exception:
        # El detalle técnico (salida de mysqldump, rutas) va solo a server.log.
        logger.exception('Error al generar el respaldo', extra={'request': request})
        messages.error(request, 'No se pudo generar el respaldo. El detalle quedó en el registro del servidor.')
        return redirect('respaldar_bd')

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

        respaldo_previo = None  # nombre del respaldo de emergencia, si llega a generarse
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
                respaldo_previo = os.path.basename(generar_respaldo_mysql())  # Si esto falla, NO restauramos
            except Exception:
                # Si no podemos hacer el respaldo de seguridad, ABORTAMOS la misión.
                # Es mejor no restaurar que restaurar sin red de seguridad.
                logger.exception('Error al crear el respaldo de seguridad previo a restaurar',
                                 extra={'request': request})
                if os.path.exists(ruta_absoluta): os.remove(ruta_absoluta)  # Limpieza
                messages.error(request, 'Operación cancelada: no se pudo crear el respaldo de seguridad '
                                        'previo, así que la base no se tocó.')
                return redirect('restaurar_bd')

            # ====================================================
            # LA RESTAURACIÓN: El momento de la verdad
            # ====================================================
            restaurar_bd_mysql(ruta_absoluta)
            # Después de restaurar: la restauración reemplaza la tabla de eventos.
            registrar_evento('restauracion_ejecutada', request.user, 'base_de_datos', None,
                             'Base de datos restaurada desde un archivo .sql, con respaldo previo')

            # Si llegamos aquí, es porque salió bien
            messages.success(request, f"¡Éxito! La base de datos fue restaurada con el archivo: {archivo.name}")

            # Limpieza: Borrar el archivo que subimos para restaurar
            if os.path.exists(ruta_absoluta):
                os.remove(ruta_absoluta)

        except Exception:
            # El detalle técnico (salida de mysql, rutas) va solo a server.log.
            logger.exception('Error en la restauración de la base de datos', extra={'request': request})
            mensaje = ('La restauración falló. La base puede haber quedado restaurada en parte: '
                       'revisa el registro del servidor antes de seguir.')
            if respaldo_previo:
                # Solo el nombre del archivo: la carpeta del servidor no se menciona (03-04, decisión 9-A).
                mensaje += f' El respaldo de seguridad previo es {respaldo_previo}.'
            messages.error(request, mensaje)

        return redirect('restaurar_bd')

    # Si es GET, solo mostramos el formulario
    return render(request, 'pedidos/restaurar_bd.html')

@login_required
@user_passes_test(es_superusuario)
def estadisticas_bd(request):
    """
    Vista de Análisis de Base de Datos.
    Calcula KPIs de crecimiento y genera las coordenadas para el gráfico SVG.
    """
    # 0. GATILLO: Asegurar que tenemos el dato de hoy
    registrar_metricas_diarias()

    # ==========================================
    # 1. KPI: ÚLTIMO RESPALDO (Lectura de Disco)
    # ==========================================
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    ultimo_respaldo_fecha = None
    ultimo_respaldo_status = "No hay respaldos"

    if os.path.exists(backup_dir):
        # Buscamos el archivo .sql más reciente
        archivos = [
            os.path.join(backup_dir, f)
            for f in os.listdir(backup_dir)
            if f.endswith('.sql')
        ]
        if archivos:
            mas_reciente = max(archivos, key=os.path.getmtime)
            timestamp = os.path.getmtime(mas_reciente)
            ultimo_respaldo_fecha = datetime.fromtimestamp(timestamp)
            ultimo_respaldo_status = "Copia de seguridad exitosa"

    # ==========================================
    # 2. KPI: CRECIMIENTO Y TAMAÑO ACTUAL
    # ==========================================
    # Obtenemos el historial completo ordenado cronológicamente
    historial = HistorialBD.objects.all().order_by('fecha_registro')

    if historial.exists():
        ultimo_registro = historial.last()
        tamano_actual_mb = ultimo_registro.tamano_mb

        # Crecimiento vs mes anterior (aprox 30 registros atrás)
        count = historial.count()
        if count > 30:
            registro_anterior = historial[count - 30]
            peso_anterior = registro_anterior.tamano_mb
            if peso_anterior > 0:
                crecimiento_pct = ((tamano_actual_mb - peso_anterior) / peso_anterior) * 100
            else:
                crecimiento_pct = 100
        else:
            # Si hay menos de un mes, comparamos con el primero que tengamos
            primer_registro = historial.first()
            peso_inicial = primer_registro.tamano_mb
            if peso_inicial > 0 and peso_inicial != tamano_actual_mb:
                crecimiento_pct = ((tamano_actual_mb - peso_inicial) / peso_inicial) * 100
            else:
                crecimiento_pct = 0
    else:
        # Valores por defecto si es el primer día de uso
        tamano_actual_mb = 0
        crecimiento_pct = 0

    # ==========================================
    # 3. LÓGICA DEL GRÁFICO SVG (GEOMETRÍA)
    # ==========================================
    # Tomamos los últimos 6 registros para el gráfico (o los que haya)
    datos_grafico = historial.order_by('-fecha_registro')[:6][::-1]

    puntos_svg = ""  # Para la línea <path d="...">
    area_svg = ""  # Para el relleno degradado
    lista_puntos = []  # Para los círculos interactivos
    max_y = 100  # Valor máximo del eje Y (por defecto)

    if datos_grafico:
        # 1. Determinar Escala Vertical (Eje Y)
        valores = [float(d.tamano_mb) for d in datos_grafico]
        max_val = max(valores)
        # Le damos un 20% de aire arriba para que el punto más alto no toque el techo
        max_y = max_val * 1.2 if max_val > 0 else 10

        # 2. Configuración del Canvas SVG (según code.html)
        # viewBox="0 0 1000 400"
        canvas_height = 400
        canvas_width = 1000
        # Margenes internos para que no se corte el gráfico
        padding_top = 50
        padding_bottom = 50
        util_height = canvas_height - padding_top - padding_bottom

        # 3. Calcular coordenadas X, Y para cada punto
        coords = []
        cantidad_puntos = len(datos_grafico)
        step_x = canvas_width / (cantidad_puntos - 1) if cantidad_puntos > 1 else canvas_width / 2

        for i, dato in enumerate(datos_grafico):
            # EJE X: Distribuido uniformemente
            if cantidad_puntos == 1:
                cx = 500  # Si es uno solo, al centro
            else:
                cx = i * step_x

            # EJE Y: Regla de tres inversa (0 está arriba en SVG)
            # Valor 0 MB -> Y = 350 (Abajo)
            # Valor Max MB -> Y = 50 (Arriba)
            valor = float(dato.tamano_mb)
            cy = (canvas_height - padding_bottom) - ((valor / max_y) * util_height)

            coords.append(f"{cx},{cy}")

            # Guardamos datos para los círculos/tooltips en el HTML
            lista_puntos.append({
                'x': cx,
                'y': cy,
                'label': dato.fecha_registro.strftime("%d %b"),  # Ej: "06 Feb"
                'valor': valor
            })

        # 4. Construir el Path SVG (Comando 'd')
        # M = Mover a, L = Línea a
        puntos_svg = "M " + " L ".join(coords)

        # 5. Construir el Área de Relleno (Cerrar el shape hacia abajo)
        # Bajamos verticalmente al fondo (V 400), volvemos al inicio (H 0) y cerramos (Z)
        area_svg = f"{puntos_svg} V {canvas_height} H 0 Z"

    context = {
        # KPIs
        'tamano_actual_mb': tamano_actual_mb,
        'crecimiento_pct': round(crecimiento_pct, 1),
        'ultimo_respaldo_fecha': ultimo_respaldo_fecha,
        'ultimo_respaldo_status': ultimo_respaldo_status,

        # Gráfico SVG
        'puntos_svg': puntos_svg,  # Línea amarilla
        'area_svg': area_svg,  # Relleno degradado
        'lista_puntos': lista_puntos,  # Círculos
        'max_y_label': round(max_y, 1),  # Etiqueta superior del eje Y
        'mitad_y_label': round(max_y / 2, 1)  # Etiqueta media
    }

    return render(request, 'pedidos/estadisticas_bd.html', context)

# ==========================================
# GESTIÓN DE PAGOS
# ==========================================

@login_required
def lista_pagos(request):
    """
    Vista para listar el historial de pagos.
    """
    # 1. Organizamos los pagos por ID para mostrarlos de forma descendente
    pagos = Pago.objects.select_related('pedido', 'pedido__cliente').all().order_by('-id')

    # 2. Paginación (10 por página)
    paginator = Paginator(pagos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 3. Renderizado
    return render(request, 'pedidos/pago_list.html', {'pagos': page_obj})

@login_required
def ingresar_pago(request, pedido_id=None):
    """
    Vista para registrar un nuevo pago.
    Puede venir con un pedido pre-seleccionado (desde el detalle) o vacío.
    """
    pedido_obj = None
    initial_data = {}

    # 1. Lógica GET (Pre-llenado)
    if pedido_id:
        pedido_obj = get_object_or_404(Pedido, pk=pedido_id)
        initial_data = {
            'pedido': pedido_obj,
            'monto': pedido_obj.saldo_pendiente  # Sugerimos pagar el total restante
        }

    estado_envio, token = None, None

    if request.method == 'POST':
        # Envío único (03-04, AUD-04-001): un envío repetido termina donde terminó el primero.
        estado_envio, token, _ = envio_unico.estado(request, 'pago')
        if estado_envio == envio_unico.USADO:
            return redirect('lista_pagos')

        form = PagoForm(request.POST)
        if estado_envio == envio_unico.INVALIDO:
            _avisar_formulario_vencido(request)
        elif form.is_valid():
            # El pago, el estado financiero del pedido y el evento van juntos (03-03, AUD-02-004).
            with transaction.atomic():
                pago = form.save(commit=False)
                pago.registrado_por = request.user
                pago.save()

                pedido_relacionado = pago.pedido
                actualizar_estado_pago_pedido(pedido_relacionado)
                registrar_evento('pago_registrado', request.user, 'pago', pago.pk,
                                 f'Pago #{pago.pk} registrado en el pedido #{pedido_relacionado.pk}')

            messages.success(request, f"Pago de ${pago.monto} registrado correctamente.")
            envio_unico.consumir(request, token, pago.pk)
            return redirect('lista_pagos')
    else:
        form = PagoForm(initial=initial_data)

    return render(request, 'pedidos/pago_form.html', {
        'form': form,
        'pedido_obj': pedido_obj,
        'token_envio': token if estado_envio == envio_unico.NUEVO else envio_unico.emitir(request, 'pago'),
    })

@login_required
def editar_pago(request, pk):
    """
    Permite modificar un pago existente (ej: corregir monto o metodo).
    Recalcula la deuda del pedido al guardar.
    """
    pago = get_object_or_404(Pago, pk=pk)
    pedido_asociado = pago.pedido

    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            # El pago y el estado de los pedidos afectados van juntos (03-03, R12). `pedido_asociado`
            # se leyó antes de armar el formulario, así que sigue siendo el pedido anterior del pago.
            with transaction.atomic():
                pago_guardado = form.save()

                # CRÍTICO: Recalcular estado del pedido porque el monto pudo cambiar
                actualizar_estado_pago_pedido(pago_guardado.pedido)
                if pedido_asociado.pk != pago_guardado.pedido_id:
                    # El pago cambió de pedido: el anterior también deja de contarlo.
                    actualizar_estado_pago_pedido(pedido_asociado)
                registrar_evento('pago_modificado', request.user, 'pago', pago_guardado.pk,
                                 f'Pago #{pago_guardado.pk} modificado en el pedido #{pago_guardado.pedido_id}')

            messages.success(request, 'Pago actualizado correctamente.')
            return redirect('detalle_pedido', pago_guardado.pedido.id)
    else:
        form = PagoForm(instance=pago)

    return render(request, 'pedidos/pago_form.html', {
        'form': form,
        'pedido_obj': pedido_asociado,
        'titulo': f'Editar Pago #{pago.id}'  # Para cambiar el título en el HTML
    })

@login_required
def eliminar_pago(request, pk):
    """
    Elimina un pago y actualiza el estado del pedido asociado.
    (Ej: Si borras el pago que completaba la deuda, el pedido vuelve a 'PARCIAL').
    """
    pago = get_object_or_404(Pago, pk=pk)
    pedido = pago.pedido  # Guardamos la referencia antes de borrarlo

    if request.method == 'POST':
        monto_eliminado = pago.monto
        # Borrar el pago y recalcular el pedido son una sola unidad (03-03).
        with transaction.atomic():
            pago.delete()

            # CRÍTICO: Recalcular estado del pedido tras la eliminación
            actualizar_estado_pago_pedido(pedido)
            registrar_evento('pago_eliminado', request.user, 'pago', pk,
                             f'Pago #{pk} eliminado del pedido #{pedido.pk}')

        messages.warning(request, f'Se eliminó el pago de ${monto_eliminado}. El saldo del pedido ha sido actualizado.')
        return redirect('detalle_pedido', pedido.id)

    return render(request, 'pedidos/pago_confirm_delete.html', {'pago': pago})

@login_required
def detalle_pago(request, pk):
    """
    Vista para ver el comprobante/detalle de un pago específico.
    """
    pago = get_object_or_404(Pago, pk=pk)
    return render(request, 'pedidos/pago_detail.html', {'pago': pago})

@login_required
def estadisticas_pagos(request):
    """
    Vista de Dashboard Financiero.
    Calcula KPIs, Barras de Progreso y Tabla de Deudores (ULTRA OPTIMIZADO).
    """

    # =========================================================================
    # PASO 0: PREPARAR EL TERRENO (La "Query Maestra")
    # =========================================================================
    pedidos_financieros = Pedido.objects.annotate(
        pagado_db=Coalesce(Sum('pagos__monto'), Value(0), output_field=IntegerField())
    ).annotate(
        saldo_db=F('valor_venta') - F('pagado_db')
    )

    # =========================================================================
    # SECCIÓN 1: KPIs (TARJETAS SUPERIORES) - Optimizado de 5 queries a 1
    # =========================================================================
    kpis = pedidos_financieros.aggregate(
        deuda_critica_total=Sum('saldo_db', filter=Q(estado='TERMINADO', saldo_db__gt=0)),
        deuda_critica_cantidad=Count('id', filter=Q(estado='TERMINADO', saldo_db__gt=0)),
        riesgo_total_monto=Sum('valor_venta', filter=Q(estado='EN_PROCESO', pagado_db=0)),
        riesgo_cantidad=Count('id', filter=Q(estado='EN_PROCESO', pagado_db=0)),
        proyeccion_total=Sum('saldo_db', filter=Q(saldo_db__gt=0)),
    )

    deuda_critica_total = kpis['deuda_critica_total'] or 0
    deuda_critica_cantidad = kpis['deuda_critica_cantidad'] or 0
    riesgo_total_monto = kpis['riesgo_total_monto'] or 0
    riesgo_cantidad = kpis['riesgo_cantidad'] or 0
    proyeccion_total = kpis['proyeccion_total'] or 0

    # =========================================================================
    # SECCIÓN 2: BARRAS DE PROGRESO - Optimizado de 3 queries a 1
    # =========================================================================
    activos_qs = pedidos_financieros.exclude(estado='ENTREGADO')

    agregados_activos = activos_qs.aggregate(
        total=Count('id'),
        pagados=Count('id', filter=Q(saldo_db__lte=0)),
        sin_abono=Count('id', filter=Q(pagado_db=0))
    )

    total_activos = agregados_activos['total'] or 0
    pagados_count = agregados_activos['pagados'] or 0
    sin_abono_count = agregados_activos['sin_abono'] or 0

    if total_activos > 0:
        pct_pagados = int((pagados_count / total_activos) * 100)
        pct_sin_abono = int((sin_abono_count / total_activos) * 100)

        # Parciales es el remanente
        parcial_count = total_activos - (pagados_count + sin_abono_count)
        pct_parcial = 100 - (pct_pagados + pct_sin_abono)
        if pct_parcial < 0: pct_parcial = 0
    else:
        pct_pagados = pct_sin_abono = pct_parcial = 0
        pagados_count = sin_abono_count = parcial_count = 0

    # =========================================================================
    # SECCIÓN 3: TABLA DE GESTIÓN (TOP DEUDORES) - Optimizado (Cero N+1)
    # =========================================================================
    # CRÍTICO: Agregamos select_related('cliente') para que el HTML no bombardee la BD
    deudores_list = pedidos_financieros.filter(
        estado='TERMINADO',
        saldo_db__gt=0
    ).select_related('cliente').order_by('fecha_entrega')

    hoy = timezone.now().date()

    # =========================================================================
    # NUEVO KPI: INGRESOS REALES DEL MES EN CURSO
    # =========================================================================
    ahora = timezone.now()
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes_actual = Pago.objects.filter(fecha__gte=inicio_mes).aggregate(total=Sum('monto'))['total'] or 0

    # =========================================================================
    # CONTEXTO FINAL
    # =========================================================================
    context = {
        'deuda_critica_total': deuda_critica_total,
        'deuda_critica_cantidad': deuda_critica_cantidad,
        'riesgo_total_monto': riesgo_total_monto,
        'riesgo_cantidad': riesgo_cantidad,
        'proyeccion_total': proyeccion_total,
        'ingresos_mes_actual': ingresos_mes_actual,
        'pct_pagados': pct_pagados,
        'count_pagados': pagados_count,
        'pct_parcial': pct_parcial,
        'count_parcial': parcial_count,
        'pct_sin_abono': pct_sin_abono,
        'count_sin_abono': sin_abono_count,
        'deudores_list': deudores_list,
        'hoy': hoy,
    }

    return render(request, 'pedidos/estadisticas_pagos.html', context)

# ==========================================
# GESTIÓN DE ERRORES HTTP
# ==========================================

def error_404(request, exception):
    return render(request, 'pedidos/errors/404.html', status=404)

def error_500(request):
    return render(request, 'pedidos/errors/500.html', status=500)


@login_not_required
@require_safe
def robots_txt(request):
    """Pide a los buscadores no indexar la app. Es pública y no renderiza plantillas."""
    return HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain; charset=utf-8")
