from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User

# Clase básica de Clientes
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

# Clase de Pedidos hecha a la medida
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('TERMINADO', 'Terminado'),
        ('ENTREGADO', 'Entregado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")

    # --- TUS CAMPOS ORIGINALES RESTAURADOS ---
    resumen_pedido = models.CharField(max_length=150, verbose_name="Resumen del Pedido")
    detalles_pedido = models.TextField(verbose_name="Detalles Técnicos", blank=True, null=True)
    imagen_referencia = models.ImageField(upload_to='referencias/', blank=True, null=True, verbose_name="Imagen Referencia")

    fecha_solicitud = models.DateTimeField(default=timezone.now, verbose_name="Fecha Solicitud")
    fecha_entrega = models.DateField(verbose_name="Fecha de Entrega", blank=True, null=True)

    valor_venta = models.PositiveIntegerField(verbose_name="Valor Total ($)", default=0)

    # --- CAMPO LEGACY (NO BORRAR AÚN) ---
    valor_abonado = models.PositiveIntegerField(verbose_name="Abono Inicial (LEGACY)", default=0)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado Operativo")

    ESTADO_PAGO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PARCIAL', 'Abono Parcial'),
        ('PAGADO', 'Pagado Total'),
    ]
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE', verbose_name="Estado Financiero")

    prioridad = models.IntegerField(default=1, verbose_name="Prioridad (1-3)")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre}"

    # --- NUEVAS PROPIEDADES CALCULADAS (CON TUS NOMBRES CORRECTOS) ---

    @property
    def total_pagado_real(self):
        """Suma todos los registros de la tabla Pago relacionados a este pedido."""
        total = self.pagos.aggregate(total=Sum('monto'))['total']
        return total if total is not None else 0

    @property
    def saldo_pendiente(self):
        """Calcula cuánto falta por pagar."""
        # Corregido para usar 'valor_venta' en lugar de 'precio_total'
        return self.valor_venta - self.total_pagado_real

    @property
    def porcentaje_pagado(self):
        """Para barras de progreso."""
        if self.valor_venta == 0: return 100
        return int((self.total_pagado_real / self.valor_venta) * 100)

# Clase de Pagos (Nueva)
class Pago(models.Model):
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('DEBITO', 'Tarjeta Débito'),
        ('CREDITO', 'Tarjeta Crédito'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos', verbose_name="Pedido Asociado")
    monto = models.PositiveIntegerField(verbose_name="Monto ($)")
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")
    metodo = models.CharField(max_length=50, choices=METODOS_PAGO, default='EFECTIVO', verbose_name="Método de Pago")
    nota = models.TextField(blank=True, null=True, verbose_name="Nota Interna")
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name="Registrado por")

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago #{self.id} - ${self.monto} ({self.get_metodo_display()})"

# Clase minimizada de Productos
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

# Clase de Cotizaciones, espejo de Pedidos
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

# Clase preparada para guardar estadísticas de uso de la base de datos
class HistorialBD(models.Model):
    """
    Modelo técnico para registrar el crecimiento de la base de datos a lo largo del tiempo.
    Se llena automáticamente una vez al día para generar gráficos de tendencia.
    """
    fecha_registro = models.DateTimeField(auto_now_add=True)
    tamano_mb = models.DecimalField(max_digits=10, decimal_places=2, help_text="Tamaño ocupado en Megabytes")

    # Métricas de contexto (para correlacionar crecimiento con actividad)
    total_pedidos = models.IntegerField(default=0)
    total_clientes = models.IntegerField(default=0)
    total_cotizaciones = models.IntegerField(default=0)
    total_productos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.fecha_registro.strftime('%d/%m/%Y')} - {self.tamano_mb} MB"