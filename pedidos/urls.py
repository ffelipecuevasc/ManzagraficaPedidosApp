from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    path('<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pk>/cambiar/<str:nuevo_estado>/', views.cambiar_estado_pedido, name='cambiar_estado'),
    path('pedido/editar/<int:pk>/', views.editar_pedido, name='editar_pedido'),
    path('pedido/eliminar/<int:pk>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
]