from django import forms
from .models import Clientes, OrdenesDeImpresion, Items, Impresoras # Ensure Impresoras is imported

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
    # ***** CORRECCIÓN DE INDENTACIÓN AQUÍ Y LAS SIGUIENTES LÍNEAS *****
    # Estas líneas deberían estar al mismo nivel de indentación que `nombre_cliente` y `tipo_impresion`
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


class OrderUpdateForm(forms.ModelForm):
    # Add fields here that are not directly from the model or need custom widgets/logic
    # For example, if you want to show client name but not make it editable directly in this form:
    # nombre_cliente = forms.CharField(label='Nombre del Cliente', disabled=True, required=False)

    # To allow unassigning the printer, make the field not required and add an empty label
    id_impresora_asignada = forms.ModelChoiceField(
        queryset=Impresoras.objects.all().order_by('nombre_impresora'),
        required=False, # Allow unassigning
        label='Impresora Asignada',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        empty_label="-- Ninguna --"
    )

    # Display current file, but don't handle re-upload in this version of the form for simplicity
    # The view will need to populate this field's initial value.
    current_archivo_adjunto = forms.CharField(
        label='Archivo Adjunto Actual',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 bg-gray-100 text-gray-500'})
    )
    # Optional: Add a new FileField if you want to allow replacement
    # nuevo_archivo_adjunto = forms.FileField(label='Reemplazar Archivo (Opcional)', required=False)


    class Meta:
        model = OrdenesDeImpresion
        fields = [
            'tipo_impresion', 'cantidad_copias', 'fecha_entrega_solicitada',
            'material_solicitado', 'observaciones_cliente', 'estado_orden',
            'id_impresora_asignada',
            # Add more fields from OrdenesDeImpresion model as needed for update
            # e.g., 'fecha_entrega_estimada', 'prioridad', 'costo_total_estimado'
        ]
        widgets = {
            'tipo_impresion': forms.Select(
                choices=OrderCreationForm.TIPO_IMPRESION_CHOICES, # Reuse choices
                attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}
            ),
            'cantidad_copias': forms.NumberInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'fecha_entrega_solicitada': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'material_solicitado': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'observaciones_cliente': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'estado_orden': forms.Select( # Define choices for estado_orden
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('en_proceso', 'En Proceso'),
                    ('completada', 'Completada'),
                    ('cancelada', 'Cancelada'),
                    ('en_pausa', 'En Pausa'),
                    # Add other relevant statuses
                ],
                attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}
            ),
        }
        labels = {
            'tipo_impresion': 'Tipo de Impresión',
            'cantidad_copias': 'Cantidad de Copias',
            'fecha_entrega_solicitada': 'Fecha de Entrega Solicitada',
            'material_solicitado': 'Material Solicitado (Opcional)',
            'observaciones_cliente': 'Observaciones del Cliente',
            'estado_orden': 'Estado de la Orden',
        }

    def __init__(self, *args, **kwargs):
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        # Populate the current_archivo_adjunto field if an instance is provided
        if self.instance and self.instance.pk and self.instance.archivo_adjunto_ruta:
            self.fields['current_archivo_adjunto'].initial = self.instance.archivo_adjunto_ruta

        # Set common error messages if needed, similar to other forms
        self.fields['cantidad_copias'].widget.attrs['min'] = 1 # Ensure min attribute if not covered by model validation
        # Add other error messages as needed
        self.fields['estado_orden'].error_messages = {'required': 'El estado de la orden es obligatorio.'}


class AssignPrinterToOrderForm(forms.Form):
    orden_a_asignar = forms.ModelChoiceField(
        queryset=OrdenesDeImpresion.objects.filter(estado_orden='pendiente').order_by('fecha_creacion_orden'),
        label='Seleccionar Orden Pendiente',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        empty_label="Seleccionar Orden..."
    )
    impresora_disponible = forms.ModelChoiceField(
        queryset=Impresoras.objects.filter(estado_impresora='disponible').order_by('nombre_impresora'),
        label='Seleccionar Impresora Disponible',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        empty_label="Seleccionar Impresora..."
    )

    def __init__(self, *args, **kwargs):
        super(AssignPrinterToOrderForm, self).__init__(*args, **kwargs)
        self.fields['orden_a_asignar'].error_messages = {'required': 'Debe seleccionar una orden.'}
        self.fields['impresora_disponible'].error_messages = {'required': 'Debe seleccionar una impresora.'}

    # Optional: Add a clean method if further validation between fields is needed,
    # e.g., check if the selected printer type is compatible with the order type,
    # but that would require more detailed printer capability data.


class UpdatePrinterStatusForm(forms.Form):
    PRINTER_STATUS_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En Mantenimiento'),
        ('fuera_de_servicio', 'Fuera de Servicio'),
    ]

    impresora_a_actualizar = forms.ModelChoiceField(
        queryset=Impresoras.objects.all().order_by('nombre_impresora'),
        label='Seleccionar Impresora',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        empty_label="Seleccionar Impresora..."
    )
    nuevo_estado_impresora = forms.ChoiceField(
        choices=PRINTER_STATUS_CHOICES,
        label='Nuevo Estado de la Impresora',
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500'})
    )

    def __init__(self, *args, **kwargs):
        super(UpdatePrinterStatusForm, self).__init__(*args, **kwargs)
        self.fields['impresora_a_actualizar'].error_messages = {'required': 'Debe seleccionar una impresora.'}
        self.fields['nuevo_estado_impresora'].error_messages = {'required': 'Debe seleccionar un nuevo estado para la impresora.'}
