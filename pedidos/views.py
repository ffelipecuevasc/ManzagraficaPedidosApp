from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Pedido, Cliente
from .forms import PedidoForm, ClienteForm
from .decorators import transaccion_segura


@login_required
def dashboard(request):
    # ==========================================
    # 1. KPIs FINANCIEROS (Dinero)
    # ==========================================

    # Ingresos Totales: Suma de valor_venta de todo lo TERMINADO (Plata segura)
    ingresos_totales = Pedido.objects.filter(estado='TERMINADO').aggregate(
        total=Sum('valor_venta')
    )['total'] or 0  # El 'or 0' es por si no hay pedidos, para que no devuelva None

    # Por Cobrar: Suma de (Venta - Abonado) de lo NO terminado (Plata en la calle)
    # Usamos 'F' para restar columnas fila por fila
    por_cobrar = Pedido.objects.filter(
        estado__in=['PENDIENTE', 'EN_PROCESO']
    ).aggregate(
        total=Sum(F('valor_venta') - F('valor_abonado'))
    )['total'] or 0

    # ==========================================
    # 2. MÉTRICAS OPERATIVAS (Conteos)
    # ==========================================
    total_clientes = Cliente.objects.count()

    # Conteos por estado para el Gráfico de Dona 1
    pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
    en_proceso = Pedido.objects.filter(estado='EN_PROCESO').count()
    completados = Pedido.objects.filter(estado='TERMINADO').count()

    # ==========================================
    # 3. DATOS PARA GRÁFICOS (Listas limpias)
    # ==========================================

    # Gráfico 1: Estado de Pedidos
    # Pasamos los datos ordenados para que coincidan con los labels
    grafico_estados_labels = ['Pendientes', 'En Proceso', 'Terminados']
    grafico_estados_data = [pendientes, en_proceso, completados]

    # Gráfico 2: Top 5 Clientes (Dona/Torta)
    # Obtenemos los 5 clientes con más pedidos
    top_clientes_qs = Cliente.objects.annotate(
        num_pedidos=Count('pedido')
    ).order_by('-num_pedidos')[:5]

    # Convertimos el QuerySet a listas simples de Python para Chart.js
    grafico_clientes_labels = [c.nombre for c in top_clientes_qs]
    grafico_clientes_data = [c.num_pedidos for c in top_clientes_qs]

    # ==========================================
    # 4. CONTEXTO FINAL
    # ==========================================
    context = {
        # KPIs Tarjetas Superiores
        'ingresos_totales': ingresos_totales,
        'por_cobrar': por_cobrar,
        'total_clientes': total_clientes,

        # Datos Crudos (por si acaso)
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'completados': completados,

        # Listas listas para Chart.js (Frontend)
        'grafico_estados_labels': grafico_estados_labels,
        'grafico_estados_data': grafico_estados_data,
        'grafico_clientes_labels': grafico_clientes_labels,
        'grafico_clientes_data': grafico_clientes_data,
    }

    return render(request, 'pedidos/dashboard.html', context)

@login_required
@transaccion_segura
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PedidoForm()
        cliente_form = ClienteForm()
    
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

def error_404(request, exception):
    return render(request, 'pedidos/errors/404.html', status=404)

def error_500(request):
    return render(request, 'pedidos/errors/500.html', status=500)
