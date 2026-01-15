from django import forms
from .models import Pedido, Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            # CAMBIO: TextInput para evitar que el navegador exija un "@"
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: correo@ejemplo.com o "No registrado"'
            }),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'resumen_pedido', 'detalles_pedido', 'valor_venta', 'valor_abonado', 'fecha_entrega']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'Busque un cliente...'}),
            'resumen_pedido': forms.TextInput(attrs={'class': 'form-control'}),
            'detalles_pedido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_abonado': forms.NumberInput(attrs={'class': 'form-control'}),
        }