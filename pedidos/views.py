from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Pedido, Cliente
from .forms import PedidoForm, ClienteForm

@login_required
def dashboard(request):
    total_pedidos = Pedido.objects.count()
    pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
    en_proceso = Pedido.objects.filter(estado='EN_PROCESO').count()
    completados = Pedido.objects.filter(estado='TERMINADO').count()
    
    # Base QuerySet
    ultimos_pedidos = Pedido.objects.all().order_by('-fecha_solicitud')

    # Filtro por Estado
    estado_filter = request.GET.get('estado')
    if estado_filter:
        ultimos_pedidos = ultimos_pedidos.filter(estado=estado_filter)
    
    # Búsqueda
    busqueda = request.GET.get('busqueda')
    if busqueda:
        ultimos_pedidos = ultimos_pedidos.filter(
            Q(cliente__nombre__icontains=busqueda) | 
            Q(cliente__telefono__icontains=busqueda)
        )

    paginator = Paginator(ultimos_pedidos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_pedidos': total_pedidos,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'completados': completados,
        'page_obj': page_obj,
        'estado_filter': estado_filter,
        'busqueda': busqueda,
    }

    return render(request, 'pedidos/dashboard.html', context)

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PedidoForm()
    
    return render(request, 'pedidos/pedido_form.html', {'form': form})

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
    clientes = Cliente.objects.all()
    return render(request, 'pedidos/cliente_list.html', {'clientes': clientes})

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
        return redirect('lista_clientes')
    return render(request, 'pedidos/cliente_confirm_delete.html', {'cliente': cliente})
