from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, help_text='Formato WhatsApp')
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('TERMINADO', 'Terminado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    resumen_pedido = models.CharField(max_length=100)
    detalles_pedido = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    valor_venta = models.IntegerField()
    valor_abonado = models.IntegerField(default=0)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateField()

    @property
    def valor_pendiente(self):
        return self.valor_venta - self.valor_abonado

    def __str__(self):
        return f"{self.resumen_pedido} - {self.cliente.nombre}"
