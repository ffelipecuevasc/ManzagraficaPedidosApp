from django import forms
from .models import Pedido, Cliente, Cotizacion, Producto, Pago


class ErroresAccesiblesMixin:
    """Enlaza cada campo con error a su mensaje (03-04, AGENTS.md 8.17).

    La plantilla escribe el mensaje con `id="error-<campo>"` y `role="alert"`; aquí el campo recibe
    `aria-invalid` y `aria-describedby` para que un lector de pantalla los una. Se aplica al validar,
    en la copia de campos de cada formulario.
    """

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            campo = self.fields.get(nombre)
            if campo is not None:
                campo.widget.attrs.update({'aria-invalid': 'true', 'aria-describedby': f'error-{nombre}'})


class ClienteForm(ErroresAccesiblesMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            # Mantenemos placeholder porque es un atributo útil de guía, no solo estilo
            'email': forms.TextInput(attrs={'placeholder': 'Ej: correo@ejemplo.com o "No registrado"'}),
        }

class CotizacionForm(ErroresAccesiblesMixin, forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['cliente', 'resumen', 'detalles', 'valor_total', 'validez', 'fecha_emision']
        widgets = {
            # Solo definimos el TIPO de input para que el navegador sepa qué calendario mostrar
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
        }

class PedidoForm(ErroresAccesiblesMixin, forms.ModelForm):
    # CAMPO VIRTUAL: No existe en el modelo Pedido, sirve para crear el Pago automáticamente
    abono_inicial = forms.IntegerField(
        required=False,
        initial=0,
        label="Abono Inicial ($)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
    )

    class Meta:
        model = Pedido
        exclude = ['fecha_solicitud', 'creado_por', 'estado_pago', 'estado', 'prioridad']

        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select select2'}),
            'resumen_pedido': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Tarjetas de Presentación'}),
            'detalles_pedido': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),

            # Aseguramos que sea DateInput para que coincida con tu BD DateField
            'fecha_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            'valor_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'estado' y 'prioridad' se eliminan de widgets porque ya no están en el form
        }

    def clean_abono_inicial(self):
        """Validar que el abono no sea mayor al total."""
        abono = self.cleaned_data.get('abono_inicial') or 0
        total = self.cleaned_data.get('valor_venta') or 0

        if total > 0 and abono > total:
            raise forms.ValidationError("El abono inicial no puede ser mayor al valor total del pedido.")
        return abono

class PagoForm(ErroresAccesiblesMixin, forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['pedido', 'monto', 'metodo', 'nota']
        widgets = {
            'pedido': forms.Select(attrs={'class': 'form-select select2'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'nota': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles opcionales...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: ordenar pedidos por ID descendente para facilitar búsqueda
        self.fields['pedido'].queryset = Pedido.objects.all().order_by('-id')

class ConversionCotizacionForm(forms.Form):
    """Datos de la conversión de una cotización en pedido (03-03, AUD-02-005 y AUD-02-027).

    Valida la fecha de entrega y el abono inicial. El estado de la cotización lo comprueba la
    vista, dentro de la transacción. El método de pago se sigue leyendo de la petición, como antes.
    """
    fecha_entrega = forms.DateField(
        label="Fecha de entrega",
        error_messages={
            'required': "Indica para cuándo es el trabajo.",
            'invalid': "Escribe una fecha de entrega válida.",
        },
    )
    valor_abonado = forms.IntegerField(
        required=False,
        min_value=0,
        label="Pago inicial ($)",
        error_messages={
            'invalid': "El pago inicial debe ser un número entero, sin puntos ni decimales.",
            'min_value': "El pago inicial no puede ser negativo.",
        },
    )

    def __init__(self, *args, valor_total, **kwargs):
        super().__init__(*args, **kwargs)
        self.valor_total = valor_total

    def clean_valor_abonado(self):
        """Vacío equivale a 0. No puede superar el total, salvo que el total sea 0 (como `PedidoForm`)."""
        abono = self.cleaned_data.get('valor_abonado') or 0
        if self.valor_total > 0 and abono > self.valor_total:
            raise forms.ValidationError("El abono no puede ser mayor al valor total de la cotización.")
        return abono


class ProductoForm(ErroresAccesiblesMixin, forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'unidad', 'valor_neto', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tarjetas de Visita'}),
            'unidad': forms.Select(attrs={'class': 'form-select select2'}),  # Select estilizado
            'valor_neto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control summernote-editor', 'rows': 3}),
        }
        labels = {
            'valor_neto': 'Valor Neto (Sin IVA)',
            'unidad': 'Unidad de Medida',
        }