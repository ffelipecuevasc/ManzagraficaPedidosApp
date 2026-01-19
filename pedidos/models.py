from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, help_text='Formato WhatsApp')
    email = models.CharField(max_length=100, blank=True, null=True)

    # --- Función que permite limpiar el número telefónico al vuelo para la API WhatsApp ---
    @property
    def telefono_whatsapp(self):
        """
        Toma el teléfono (ej: '+56 9 1234-5678') y lo deja limpio
        para la URL de WhatsApp (ej: '56912345678').
        """
        if not self.telefono:
            return ""

        # Quitamos espacios, el signo +, guiones y paréntesis
        limpio = self.telefono.replace(" ", "").replace("+", "").replace("-", "").replace("(", "").replace(")", "")
        return limpio

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
    imagen_referencia = models.ImageField(upload_to='pedidos/', blank=True, null=True)

    @property
    def valor_pendiente(self):
        return self.valor_venta - self.valor_abonado

    def __str__(self):
        return f"{self.resumen_pedido} - {self.cliente.nombre}"