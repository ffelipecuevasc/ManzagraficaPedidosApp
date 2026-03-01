from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Count, Sum, F, ProtectedError, F, Value, IntegerField
from django.db.models.functions import TruncMonth, Coalesce
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import transaction
from .models import Pedido, Cliente, Cotizacion, Producto, ItemPedido, ItemCotizacion, HistorialBD, Pago
from .forms import PedidoForm, ClienteForm, CotizacionForm, ProductoForm, PagoForm
from .decorators import transaccion_segura
from .utils import generar_respaldo_mysql, restaurar_bd_mysql, registrar_metricas_diarias
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
    # 0. GATILLO DE ESTADÍSTICAS
    # ==========================================
    # Registra el peso de la BD y métricas diarias si no se ha hecho hoy.
    registrar_metricas_diarias()

    # Definimos fechas de referencia
    ahora = timezone.now()
    hoy = ahora.date()

    # ==========================================
    # 1. TARJETAS SUPERIORES (KPIs OPERATIVOS)
    # ==========================================

    # --- TARJETA 1 (VERDE): ÚLTIMO RESPALDO BD ---
    # Lógica extraída de: estadisticas_bd / utils.py
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    ultimo_respaldo_fecha = None

    if os.path.exists(backup_dir):
        # Listamos archivos .sql y buscamos el más reciente por fecha de modificación
        archivos = [
            os.path.join(backup_dir, f)
            for f in os.listdir(backup_dir)
            if f.endswith('.sql')
        ]
        if archivos:
            mas_reciente = max(archivos, key=os.path.getmtime)
            # Convertimos timestamp a datetime consciente de la zona horaria si es necesario
            ultimo_respaldo_fecha = datetime.fromtimestamp(os.path.getmtime(mas_reciente))

    # --- TARJETA 2 (ROJA): PEDIDOS ATRASADOS ---
    # Lógica extraída de: trabajo_semanal (Zona Crítica)
    # Pedidos NO terminados cuya fecha de entrega ya pasó (< hoy)
    criticos_count = Pedido.objects.exclude(estado='TERMINADO').filter(
        fecha_entrega__lt=hoy
    ).count()

    # --- TARJETA 3 (AMARILLA): PEDIDOS URGENTES (Próximos 7 días) ---
    # Lógica extraída de: trabajo_semanal (Zona Urgente)
    # Pedidos NO terminados con entrega entre hoy y hoy+7 días
    limite_semana = hoy + timedelta(days=7)
    urgentes_count = Pedido.objects.exclude(estado='TERMINADO').filter(
        fecha_entrega__range=[hoy, limite_semana]
    ).count()

    # --- TARJETA 4 (AZUL): VOLUMEN MES ACTUAL ---
    # Lógica extraída de: estadisticas_pedidos
    # Total de pedidos recibidos desde el día 1 del mes actual hasta ahora
    inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    pedidos_mes_count = Pedido.objects.filter(
        fecha_solicitud__gte=inicio_mes_actual
    ).count()

    # ==========================================
    # 2. DATOS PARA GRÁFICOS
    # ==========================================

    # A. Datos para Gráfico de Dona (AHORA FILTRADO POR MES ACTUAL)
    # Reutilizamos 'inicio_mes_actual' definido arriba para filtrar la torta
    queryset_mes = Pedido.objects.filter(fecha_solicitud__gte=inicio_mes_actual)

    total_pedidos = queryset_mes.count()  # Total solo del mes
    pendientes = queryset_mes.filter(estado='PENDIENTE').count()
    en_proceso = queryset_mes.filter(estado='EN_PROCESO').count()
    completados = queryset_mes.filter(estado='TERMINADO').count()

    # Cálculo de Porcentajes (Conic Gradient CSS)
    if total_pedidos > 0:
        pct_pendientes = (pendientes / total_pedidos) * 100
        pct_en_proceso = (en_proceso / total_pedidos) * 100
        stop_1 = pct_pendientes
        stop_2 = pct_pendientes + pct_en_proceso
    else:
        stop_1 = 0
        stop_2 = 0

    # Porcentajes texto (Redondeados para visualización)
    pct_text_pendientes = round((pendientes / total_pedidos * 100)) if total_pedidos > 0 else 0
    pct_text_proceso = round((en_proceso / total_pedidos * 100)) if total_pedidos > 0 else 0
    pct_text_completados = round((completados / total_pedidos * 100)) if total_pedidos > 0 else 0

    # B. Datos para Gráfico de Barras (Top Clientes - ESTE SE MANTIENE HISTÓRICO)
    # No aplicamos filtro de fecha aquí para mantener la fidelidad histórica
    top_clientes = Cliente.objects.annotate(
        num_pedidos=Count('pedido')
    ).order_by('-num_pedidos')[:5]

    max_pedidos = top_clientes[0].num_pedidos if top_clientes else 1

    # ==========================================
    # 3. CONTEXTO
    # ==========================================
    context = {
        # Nuevas KPIs Operativas (Tarjetas Superiores)
        'ultimo_respaldo_fecha': ultimo_respaldo_fecha,  # Tarjeta 1
        'criticos_count': criticos_count,  # Tarjeta 2
        'urgentes_count': urgentes_count,  # Tarjeta 3
        'pedidos_mes_count': pedidos_mes_count,  # Tarjeta 4

        # Datos para Gráficos (Dona y Barras - Sección Inferior)
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
    """Recalcula y guarda el estado financiero del pedido basado en sus pagos."""
    if pedido.saldo_pendiente <= 0:
        pedido.estado_pago = 'PAGADO'
    elif pedido.total_pagado_real > 0:
        pedido.estado_pago = 'PARCIAL'
    else:
        pedido.estado_pago = 'PENDIENTE'
    pedido.save()

# ==========================================
# GESTIÓN DE PEDIDOS
# ==========================================

@login_required
@transaccion_segura
def crear_pedido(request):
    cliente_form = ClienteForm()
    productos_disponibles = Producto.objects.all().order_by('nombre')
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)

        if form.is_valid():
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
                items_json = request.POST.get('items_json')
                if items_json:
                    try:
                        data_items = json.loads(items_json)
                        for item in data_items:
                            producto_obj = Producto.objects.get(pk=item['producto_id'])
                            ItemPedido.objects.create(
                                pedido=pedido,
                                producto=producto_obj,
                                cantidad=float(item['cantidad']),
                                precio_unitario=int(item['precio_unitario'])
                            )
                    except Exception as e:
                        print(f"Error procesando items: {e}")
                        # No detenemos el proceso, los items son recuperables o editables

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

                    # OJO: NO actualizamos pedido.valor_abonado.
                    # Se mantiene en 0 como solicitaste.

            return redirect('detalle_pedido', pk=pedido.pk)

        else:
            # Debugging en consola si falla la validación
            print("\n" + "=" * 30)
            print("❌ ERROR DE VALIDACIÓN DETECTADO [CREACIÓN DE PEDIDO]:")
            print(form.errors)
            print("=" * 30 + "\n")

    else:
        form = PedidoForm()

    context = {
        'form': form,
        'cliente_form': cliente_form,
        'productos_disponibles': productos_disponibles,
        'clientes': clientes,
        'productos': productos_disponibles,
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
        'items_json': json.dumps(items_list)  # ¡Aquí enviamos los datos al HTML!
    })

@login_required
@transaccion_segura
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
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
        estado='PENDIENTE',  # IMPORTANTE: Nace pendiente
        fecha_entrega=original.fecha_entrega,  # Mantenemos fecha ref, usuario editará si quiere
        imagen_referencia=original.imagen_referencia  # Mantenemos la imagen si tenía
    )

    # 3. Guardar el nuevo registro (esto genera fecha_solicitud actual automática)
    nuevo_pedido.save()

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
        year_actual = hoy.year

        # 1. Crear una plantilla de 12 meses en cero
        meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        datos_anuales = [{'mes_idx': i, 'label': meses_nombres[i - 1], 'total': 0} for i in range(1, 13)]

        # 2. Consultar la BD solo para los pedidos del año actual
        datos_bd = (
            Pedido.objects
            .filter(fecha_solicitud__year=year_actual)
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
            # Eje X e Y convertidos a INT para evitar error de comas flotantes en el HTML
            cx = int(i * step_x)
            valor = float(dato['total'])
            cy = int((canvas_height - padding_bottom) - ((valor / max_y) * util_height))

            coords.append(f"{cx},{cy}")

            # Pasamos el dato del "valor" para pintarlo como etiqueta flotante
            lista_puntos.append({
                'x': cx,
                'y': cy,
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
        'items_json': json.dumps(items_list)  # ¡Enviamos los datos!
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
    Copia el cliente, datos, productos y GENERA EL PAGO INICIAL SI EXISTE.
    """
    cotizacion = get_object_or_404(Cotizacion, pk=pk)

    if request.method == 'POST':
        # 1. Capturar datos del formulario
        fecha_entrega = request.POST.get('fecha_entrega')
        abono_input = request.POST.get('valor_abonado', 0)
        try:
            abono = int(abono_input)
        except ValueError:
            abono = 0

        # 2. Crear el Pedido (Cabecera)
        # IMPORTANTE: Inicializamos valor_abonado en 0. Si hay abono, lo sumará la lógica de Pago.
        pedido = Pedido.objects.create(
            cliente=cotizacion.cliente,
            resumen_pedido=cotizacion.resumen,
            detalles_pedido=cotizacion.detalles,
            valor_venta=cotizacion.valor_total,
            fecha_entrega=fecha_entrega,
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

        # 4. --- LÓGICA DE PAGO INICIAL (CORREGIDA) ---
        if abono > 0:
            metodo = request.POST.get('metodo_pago', 'TRANSFERENCIA')
            # A. Crear el registro en la tabla Pago
            Pago.objects.create(
                pedido=pedido,
                monto=abono,
                metodo=metodo,
                fecha=timezone.now(),
                registrado_por=request.user,
                nota=f'Abono inicial por conversión de Cotización #{cotizacion.id}'
            )

            # Calcular estado financiero
            if pedido.saldo_pendiente <= 0:
                pedido.estado_pago = 'PAGADO'
            else:
                pedido.estado_pago = 'PARCIAL'

            pedido.save()
        # ---------------------------------------------

        # 5. Cerrar la Cotización
        cotizacion.estado = 'ACEPTADA'
        cotizacion.save()

        # 6. Redirigir al nuevo pedido
        messages.success(request, f"Cotización convertida exitosamente en el Pedido #{pedido.id}")
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
    error_message = None  # Variable para guardar el mensaje de error

    if request.method == 'POST':
        try:
            producto.delete()
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
@transaccion_segura
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

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            # 2. Guardar el Pago
            pago = form.save(commit=False)
            pago.registrado_por = request.user
            pago.save()

            # 3. ACTUALIZACIÓN AUTOMÁTICA DEL PEDIDO
            pedido_relacionado = pago.pedido

            # Recalcular estado financiero
            # (Asumiendo que el modelo Pedido tiene propiedades o métodos para esto,
            #  o que actualizamos campos manuales como valor_abonado)

            # Opción A: Si usamos el campo legacy 'valor_abonado'
            # pedido_relacionado.valor_abonado += pago.monto 

            # Opción B: Si usamos propiedades calculadas en el modelo, 
            # solo necesitamos actualizar el estado 'estado_pago' si existe.
            # Aquí usaremos la función auxiliar definida arriba si aplica, 
            # o lógica directa simple:

            # Recalculamos el total pagado sumando todos los pagos (incluyendo el nuevo)
            total_pagado = pedido_relacionado.pagos.aggregate(Sum('monto'))['monto__sum'] or 0

            # Determinamos estado (si existe el campo estado_pago)
            if hasattr(pedido_relacionado, 'estado_pago'):
                if pedido_relacionado.saldo_pendiente <= 0:
                    pedido_relacionado.estado_pago = 'PAGADO'
                elif total_pagado > 0:
                    pedido_relacionado.estado_pago = 'PARCIAL'
                else:
                    pedido_relacionado.estado_pago = 'PENDIENTE'

            pedido_relacionado.save()

            messages.success(request, f"Pago de ${pago.monto} registrado correctamente.")
            return redirect('lista_pagos')
    else:
        form = PagoForm(initial=initial_data)

    return render(request, 'pedidos/pago_form.html', {
        'form': form,
        'pedido_obj': pedido_obj
    })

@login_required
@transaccion_segura
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
            pago_guardado = form.save()

            # CRÍTICO: Recalcular estado del pedido porque el monto pudo cambiar
            actualizar_estado_pago_pedido(pago_guardado.pedido)

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
@transaccion_segura
def eliminar_pago(request, pk):
    """
    Elimina un pago y actualiza el estado del pedido asociado.
    (Ej: Si borras el pago que completaba la deuda, el pedido vuelve a 'PARCIAL').
    """
    pago = get_object_or_404(Pago, pk=pk)
    pedido = pago.pedido  # Guardamos la referencia antes de borrarlo

    if request.method == 'POST':
        monto_eliminado = pago.monto
        pago.delete()

        # CRÍTICO: Recalcular estado del pedido tras la eliminación
        actualizar_estado_pago_pedido(pedido)

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
    Calcula KPIs, Barras de Progreso y Tabla de Deudores.
    """

    # =========================================================================
    # PASO 0: PREPARAR EL TERRENO (La "Query Maestra")
    # =========================================================================
    # Calculamos lo pagado y el saldo a nivel de base de datos para filtrar rápido.
    pedidos_financieros = Pedido.objects.annotate(
        pagado_db=Coalesce(Sum('pagos__monto'), Value(0), output_field=IntegerField())
    ).annotate(
        saldo_db=F('valor_venta') - F('pagado_db')
    )

    # =========================================================================
    # SECCIÓN 1: KPIs (TARJETAS SUPERIORES) - YA IMPLEMENTADO
    # =========================================================================

    # KPI 1: DEUDA CRÍTICA (Terminados sin pagar)
    kpi_critico_qs = pedidos_financieros.filter(estado='TERMINADO', saldo_db__gt=0)
    deuda_critica_total = kpi_critico_qs.aggregate(Sum('saldo_db'))['saldo_db__sum'] or 0
    deuda_critica_cantidad = kpi_critico_qs.count()

    # KPI 2: RIESGO OPERATIVO (En Proceso sin abono)
    kpi_riesgo_qs = pedidos_financieros.filter(estado='EN_PROCESO', pagado_db=0)
    riesgo_total_monto = kpi_riesgo_qs.aggregate(Sum('valor_venta'))['valor_venta__sum'] or 0
    riesgo_cantidad = kpi_riesgo_qs.count()

    # KPI 3: PROYECCIÓN (Dinero en la calle)
    proyeccion_qs = pedidos_financieros.filter(saldo_db__gt=0)
    proyeccion_total = proyeccion_qs.aggregate(Sum('saldo_db'))['saldo_db__sum'] or 0

    # =========================================================================
    # SECCIÓN 2: BARRAS DE PROGRESO (Estado de los Pedidos Activos)
    # =========================================================================
    # Consideramos "Activos" aquellos que NO estén entregados/archivados.
    activos_qs = pedidos_financieros.exclude(estado='ENTREGADO')
    total_activos = activos_qs.count()

    if total_activos > 0:
        # A. Pagados (Saldo <= 0)
        pagados_count = activos_qs.filter(saldo_db__lte=0).count()
        pct_pagados = int((pagados_count / total_activos) * 100)

        # B. Sin Abono (Pagado == 0)
        sin_abono_count = activos_qs.filter(pagado_db=0).count()
        pct_sin_abono = int((sin_abono_count / total_activos) * 100)

        # C. Parciales (El resto: tiene abono pero tiene deuda)
        # Lógica: Total - (Pagados + Sin Abono) para que sume 100% exacto visualmente
        parcial_count = total_activos - (pagados_count + sin_abono_count)
        pct_parcial = 100 - (pct_pagados + pct_sin_abono)

        # Ajuste de seguridad por si da negativo en casos raros
        if pct_parcial < 0: pct_parcial = 0

    else:
        pct_pagados = 0
        pct_sin_abono = 0
        pct_parcial = 0
        pagados_count = 0
        sin_abono_count = 0
        parcial_count = 0

    # =========================================================================
    # SECCIÓN 3: TABLA DE GESTIÓN (TOP DEUDORES)
    # =========================================================================
    # Reutilizamos el QuerySet de 'Deuda Crítica' (Terminados con deuda).
    # Ordenamos por fecha de entrega ascendente (los más viejos primero = más urgencia).
    deudores_list = kpi_critico_qs.order_by('fecha_entrega')

    # Para calcular los "Días de Atraso" usaremos la fecha de hoy en el template
    hoy = timezone.now().date()

    # =========================================================================
    # NUEVO KPI: INGRESOS REALES DEL MES EN CURSO (Caja Verde Horizontal)
    # =========================================================================
    ahora = timezone.now()
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Sumamos la tabla PAGO filtrando por fecha de pago >= inicio de este mes.
    # Esto muestra el dinero real que entró a la caja, sin importar si el pedido es viejo o nuevo.
    ingresos_mes_actual = Pago.objects.filter(fecha__gte=inicio_mes).aggregate(total=Sum('monto'))['total'] or 0

    # =========================================================================
    # CONTEXTO FINAL
    # =========================================================================
    context = {
        # KPIs
        'deuda_critica_total': deuda_critica_total,
        'deuda_critica_cantidad': deuda_critica_cantidad,
        'riesgo_total_monto': riesgo_total_monto,
        'riesgo_cantidad': riesgo_cantidad,
        'proyeccion_total': proyeccion_total,
        'ingresos_mes_actual': ingresos_mes_actual,

        # Barras de Progreso
        'pct_pagados': pct_pagados,
        'count_pagados': pagados_count,
        'pct_parcial': pct_parcial,
        'count_parcial': parcial_count,
        'pct_sin_abono': pct_sin_abono,
        'count_sin_abono': sin_abono_count,

        # Tabla y Utilidades
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