from django import forms
from .models import Clientes, OrdenesDeImpresion, Items # Ensure OrdenesDeImpresion and Items are imported

class OrderCreationForm(forms.Form):
    # Client information (simplified for now, will link to Clientes model more directly in view)
    nombre_cliente = forms.CharField(
        label='Nombre del Cliente',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )
    # Optional: Add email/phone for client if we want to create/update client details via this form
    # contacto_email_cliente = forms.EmailField(label='Email del Cliente', required=False, widget=forms.EmailInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}))
    # contacto_telefono_cliente = forms.CharField(label='Teléfono del Cliente', required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}))

    TIPO_IMPRESION_CHOICES = [
        ('', 'Seleccionar...'),
        ('blanco-negro', 'Blanco y Negro'),
        ('color', 'Color'),
        ('gran-formato', 'Gran Formato'),
    ]
    tipo_impresion = forms.ChoiceField(
        label='Tipo de Impresión',
        choices=TIPO_IMPRESION_CHOICES,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )
    cantidad_copias = forms.IntegerField(
        label='Cantidad de Copias',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )
        # New field for number of pages:
        numero_paginas_documento = forms.IntegerField(
            label='Número de Páginas del Documento',
            min_value=1,
            widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            help_text="Ingrese el número total de páginas contenidas en el archivo que subió."
        )

        fecha_entrega_solicitada = forms.DateField( # Ensure this is below the new field or placed logically
        label='Fecha de Entrega',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )
    observaciones_cliente = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )
    archivo_libro = forms.FileField(
        label='Subir Archivo Libro/Documento',
        widget=forms.FileInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )
    # For material_solicitado, keeping it simple as a text field for now.
    # Later, this could be a more complex field, possibly linking to Items model or having autocomplete.
    material_solicitado = forms.CharField(
        label='Material Solicitado (Opcional)',
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        help_text="Ej: Papel Couché 150g, Vinilo Adhesivo, etc."
    )

    def __init__(self, *args, **kwargs):
        super(OrderCreationForm, self).__init__(*args, **kwargs)
        # Basic required validation messages (Django does some by default)
        self.fields['nombre_cliente'].error_messages = {'required': 'El nombre del cliente es obligatorio.'}
        self.fields['tipo_impresion'].error_messages = {'required': 'Debe seleccionar un tipo de impresión.'}
        self.fields['cantidad_copias'].error_messages = {'required': 'La cantidad de copias es obligatoria.', 'min_value': 'La cantidad debe ser al menos 1.'}
        self.fields['numero_paginas_documento'].error_messages = {'required': 'El número de páginas del documento es obligatorio.', 'min_value': 'El documento debe tener al menos 1 página.'}
        self.fields['fecha_entrega_solicitada'].error_messages = {'required': 'Debe seleccionar una fecha de entrega.'}
        self.fields['archivo_libro'].error_messages = {'required': 'Debe subir el archivo del libro o documento.'}


class InsumoConsumptionForm(forms.Form):
    orden_consumo = forms.ModelChoiceField(
        queryset=OrdenesDeImpresion.objects.all().order_by('-fecha_creacion_orden'), # Show all orders for now
        label='Seleccionar Orden',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        empty_label="Seleccionar Orden..."
    )
    item_consumido = forms.ModelChoiceField(
        queryset=Items.objects.all().order_by('id_item'), # Show all items
        label='Tipo de Insumo',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        empty_label="Seleccionar Insumo..."
    )
    cantidad_consumida = forms.IntegerField(
        label='Cantidad Utilizada',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )

    def __init__(self, *args, **kwargs):
        super(InsumoConsumptionForm, self).__init__(*args, **kwargs)
        self.fields['orden_consumo'].error_messages = {'required': 'Debe seleccionar una orden.'}
        self.fields['item_consumido'].error_messages = {'required': 'Debe seleccionar un tipo de insumo.'}
        self.fields['cantidad_consumida'].error_messages = {'required': 'La cantidad consumida es obligatoria.', 'min_value': 'La cantidad debe ser al menos 1.'}

    # Optional: Add clean methods for further validation, e.g., ensuring selected item has enough stock,
    # but this might be better handled in the view during processing to provide more dynamic feedback
    # or to avoid re-querying stock too often.
