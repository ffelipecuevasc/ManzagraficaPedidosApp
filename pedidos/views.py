from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Pedido, Cliente
from .forms import PedidoForm, ClienteForm
from .decorators import transaccion_segura
from django.utils import timezone
from datetime import timedelta
import locale


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

@login_required
@transaccion_segura
def crear_pedido(request):
    # CORRECCIÓN: Inicializamos el form de cliente FUERA de los bloques if/else
    # Así garantizamos que la variable siempre exista, evitando el Error 500.
    cliente_form = ClienteForm()

    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PedidoForm()

    return render(request, 'pedidos/pedido_form.html', {'form': form, 'cliente_form': cliente_form})

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
@transaccion_segura
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PedidoForm(instance=pedido)
    
    return render(request, 'pedidos/pedido_form.html', {'form': form})

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

def error_404(request, exception):
    return render(request, 'pedidos/errors/404.html', status=404)

def error_500(request):
    return render(request, 'pedidos/errors/500.html', status=500)
