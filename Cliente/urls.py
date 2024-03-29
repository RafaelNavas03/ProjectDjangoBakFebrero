from django.urls import path
from .views import ActualizarClienteView,EditarCliente,VerClientesView,RealizarPedidoView

urlpatterns = [
    path('actualizar_cliente/', ActualizarClienteView.as_view(), name='actualizar_cliente'),
    path('actualizar_cliente/<int:id_cliente>/', EditarCliente.as_view(), name='actualizar_cliente'),
    path('ver_clientes/', VerClientesView.as_view(), name='ver_clientes'),
    path('realizar_pedido/<int:id_cuenta>/', RealizarPedidoView.as_view(), name='realizar_pedido')
]
