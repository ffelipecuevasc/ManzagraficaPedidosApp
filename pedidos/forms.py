from django import forms
from .models import Pedido, Cliente, Cotizacion, Producto

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
    class Meta:
        model = Pedido
        fields = ['cliente', 'resumen_pedido', 'detalles_pedido', 'valor_venta', 'valor_abonado', 'fecha_entrega', 'imagen_referencia']
        widgets = {
            # Solo definimos el TIPO de input para que el navegador sepa qué calendario mostrar
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        valor_venta = cleaned_data.get('valor_venta')
        valor_abonado = cleaned_data.get('valor_abonado')

        # Validar que el abono no supere el total
        if valor_venta is not None and valor_abonado is not None:
            if valor_abonado > valor_venta:
                self.add_error('valor_abonado', 'El abono no puede ser mayor al valor total del pedido.')

        return cleaned_data

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'unidad', 'valor_neto', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tarjetas de Visita'}),
            'unidad': forms.Select(attrs={'class': 'form-select select2'}), # Select estilizado
            'valor_neto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control summernote-editor', 'rows': 3}),
        }
        labels = {
            'valor_neto': 'Valor Neto (Sin IVA)',
            'unidad': 'Unidad de Medida',
        }