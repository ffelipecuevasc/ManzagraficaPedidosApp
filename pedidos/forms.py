from django import forms
from .models import Pedido, Cliente, Cotizacion, Producto, Pago

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            # Mantenemos placeholder porque es un atributo útil de guía, no solo estilo
            'email': forms.TextInput(attrs={'placeholder': 'Ej: correo@ejemplo.com o "No registrado"'}),
        }

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['cliente', 'resumen', 'detalles', 'valor_total', 'validez', 'fecha_emision']
        widgets = {
            # Solo definimos el TIPO de input para que el navegador sepa qué calendario mostrar
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
        }

class PedidoForm(forms.ModelForm):
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

class PagoForm(forms.ModelForm):
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

class ProductoForm(forms.ModelForm):
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