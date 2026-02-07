from django.urls import path
from .views import respaldar_bd, generar_respaldo_bd
from . import views

urlpatterns = [
    # PANEL DE CONTROL
    path('', views.dashboard, name='dashboard'),

    # PEDIDOS
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/lista/', views.lista_pedidos, name='lista_pedidos'),
    path('<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pk>/cambiar/<str:nuevo_estado>/', views.cambiar_estado_pedido, name='cambiar_estado'),
    path('pedido/duplicar/<int:pk>/', views.duplicar_pedido, name='duplicar_pedido'),
    path('pedido/editar/<int:pk>/', views.editar_pedido, name='editar_pedido'),
    path('pedido/eliminar/<int:pk>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('pedidos/trabajo-semanal/', views.trabajo_semanal, name='trabajo_semanal'),

    # CLIENTES
    path('api/cliente/nuevo/', views.api_crear_cliente_rapido, name='api_crear_cliente_rapido'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),

    # COTIZACIONES (NUEVO MÓDULO FASE A)
    path('cotizaciones/lista/', views.lista_cotizaciones, name='lista_cotizaciones'),
    path('cotizaciones/nueva/', views.crear_cotizacion, name='crear_cotizacion'),
    path('cotizaciones/detalle/<int:pk>/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('cotizaciones/editar/<int:pk>/', views.editar_cotizacion, name='editar_cotizacion'),
    path('cotizaciones/eliminar/<int:pk>/', views.eliminar_cotizacion, name='eliminar_cotizacion'),
    path('cotizaciones/convertir/<int:pk>/', views.convertir_a_pedido, name='convertir_a_pedido'),
    path('cotizaciones/<int:pk>/pdf/', views.exportar_cotizacion_pdf, name='exportar_cotizacion_pdf'),

    # PRODUCTOS
    path('productos/lista/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('api/producto/nuevo/', views.api_crear_producto_rapido, name='api_crear_producto_rapido'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),

    # GESTIÓN DE BD
    path('base_datos/respaldar_bd/', views.respaldar_bd, name='respaldar_bd'),
    path('base_datos/respaldar_bd/accion/', views.generar_respaldo_bd, name='generar_respaldo_bd'),
    path('base_datos/restaurar_bd/', views.restaurar_bd, name='restaurar_bd'),
    path('base_datos/estadisticas_bd/', views.estadisticas_bd, name='estadisticas_bd'),
]