from django.apps import AppConfig


class PedidosConfig(AppConfig):
    name = "pedidos"

    def ready(self):
        from . import senales  # noqa: F401  (conecta las señales de acceso)
