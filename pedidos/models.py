from django.db import models
from datetime import timedelta
from django.utils import timezone

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, help_text='Formato WhatsApp')
    email = models.CharField(max_length=100, blank=True, null=True)

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


class Cotizacion(models.Model):
    """
    Modelo espejo de Pedido para la Fase A: Gestión de Cotizaciones.
    """
    ESTADO_COTIZACION_CHOICES = [
        ('BORRADOR', 'Borrador'),  # Aún editando
        ('ENVIADA', 'Enviada'),  # Esperando respuesta
        ('ACEPTADA', 'Aceptada'),  # Se convirtió en pedido
        ('EXPIRADA', 'Expirada'),  # Pasó la fecha sin acción
        ('RECHAZADA', 'Rechazada'),  # Cliente no quiso
    ]

    # Relaciones y Datos Básicos
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    resumen = models.CharField(max_length=100, help_text="Título corto del trabajo")
    detalles = models.TextField(help_text="Detalles técnicos (Summernote)")

    # Datos Económicos y Temporales
    valor_total = models.IntegerField(help_text="Precio neto propuesto")
    fecha_emision = models.DateField(default=timezone.now)  # Editable si se requiere, por defecto hoy
    validez = models.IntegerField(default=15, help_text="Días de validez de la oferta")

    estado = models.CharField(max_length=20, choices=ESTADO_COTIZACION_CHOICES, default='BORRADOR')

    # Timestamps de control interno
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def fecha_vencimiento(self):
        # Ojo: fecha_emision es Date, timedelta es tiempo. Funciona directo.
        return self.fecha_emision + timedelta(days=self.validez)

    @property
    def esta_vencida(self):
        return self.estado == 'ENVIADA' and self.fecha_vencimiento < timezone.now().date()

    def __str__(self):
        return f"Cotización #{self.id} - {self.cliente.nombre}"

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


class Producto(models.Model):
    """
    Maestro de Productos / Servicios (Refactorizado con IVA 19%).
    """
    UNIDAD_CHOICES = [
        ('UNITARIO', 'Unitario'),
        ('METRO_CUADRADO', 'Metro Cuadrado (m2)'),
        ('METRO_LINEAL', 'Metro Lineal (ml)'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True, help_text="Detalles técnicos o especificaciones base")

    # Nuevo campo: Unidad de medida
    unidad = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='UNITARIO')

    # Nuevo campo: Precio Base (Neto)
    valor_neto = models.IntegerField(help_text="Valor base sin impuestos")

    # Campos Calculados (Se llenan solos en el save)
    iva = models.IntegerField(help_text="19% del valor neto", editable=False)
    valor_bruto = models.IntegerField(help_text="Precio final con IVA (Neto + IVA)", editable=False)

    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Sobrescribimos el guardar para calcular IVA y Bruto automáticamente.
        """
        # Calcular IVA (19%) - Usamos round para redondear matemáticamente antes de convertir a entero
        self.iva = int(round(self.valor_neto * 0.19))

        # Calcular Bruto
        self.valor_bruto = self.valor_neto + self.iva

        super().save(*args, **kwargs)

    def __str__(self):
        # Mostramos el precio final en el admin/selects para facilitar la vida
        return f"{self.nombre} (${self.valor_bruto} IVA inc.)"

# Clase hecha para relacionar Productos con Pedidos y viceversa.
class ItemPedido(models.Model):
    """
    Tabla intermedia para relacionar Pedidos con Productos.
    Guarda el precio histórico al momento de la venta.
    """
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    # Usamos PROTECT para que si borras un producto del catálogo, no se borren los pedidos históricos.

    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    precio_unitario = models.IntegerField(help_text="Precio al momento de la venta")

    # El subtotal se calcula, pero a veces es útil guardarlo o calcularlo al vuelo
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Pedido #{self.pedido.id}"

# Clase hecha para relacionar Productos con Cotizaciones y viceversa.
class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    # Guardamos el precio al momento de cotizar (por si sube después)
    precio_unitario = models.IntegerField(help_text="Precio al momento de cotizar")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario