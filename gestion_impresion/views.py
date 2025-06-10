from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django.db import transaction, IntegrityError

# Ensure all necessary models are imported
from .models import Items, DescripcionesMaterial, Clientes, OrdenesDeImpresion, OrdenInsumoConsumo, Impresoras
from .forms import OrderCreationForm, InsumoConsumptionForm

# ... (Placeholder Item IDs and Consumption Rates - keep them) ...
ID_ITEM_PAPEL_DEFAULT = 'S-OFF-P-BOND-090'
ID_ITEM_TINTA_NEGRA = 'T-OFF-CMYK-K'
ID_ITEM_TINTA_CYAN = 'T-OFF-CMYK-C'
ID_ITEM_TINTA_MAGENTA = 'T-OFF-CMYK-M'
ID_ITEM_TINTA_AMARILLA = 'T-OFF-CMYK-Y'
TINTA_POR_PAGINA_NEGRA = 0.02
TINTA_POR_PAGINA_COLOR_CHANNEL = 0.01

def primer_empleado_dashboard_view(request):
    insumos_list = Items.objects.select_related('descripcion_especifica').all()
    order_form = OrderCreationForm()
    consumption_form = InsumoConsumptionForm()

    # --- Logic for RF5: Ver Estado de Orden ---
    # Fetch all orders, ordered by most recent first. Include related client name for display.
    all_orders_rf5 = OrdenesDeImpresion.objects.select_related('id_cliente').order_by('-fecha_creacion_orden')
    selected_order_details_rf5 = None
    selected_orden_id_rf5_val_str = request.GET.get('selected_orden_id_rf5') # Name of the select input in HTML

    if selected_orden_id_rf5_val_str:
        try:
            # Ensure the value is an integer before querying
            selected_orden_id_rf5_int = int(selected_orden_id_rf5_val_str)
            selected_order_details_rf5 = OrdenesDeImpresion.objects.select_related(
                'id_cliente',
                'id_impresora_asignada' # To get printer details if assigned
            ).get(id_orden=selected_orden_id_rf5_int)
        except OrdenesDeImpresion.DoesNotExist:
            messages.error(request, f"La orden con ID {selected_orden_id_rf5_val_str} no fue encontrada.")
            selected_order_details_rf5 = None # Ensure it's None if not found
        except ValueError: # Handle cases where selected_orden_id_rf5_val is not a valid integer
            messages.error(request, f"El ID de orden proporcionado ({selected_orden_id_rf5_val_str}) no es válido.")
            selected_order_details_rf5 = None # Ensure it's None if ID is invalid


    if request.method == 'POST':
        if 'submit_crear_orden' in request.POST:
            order_form = OrderCreationForm(request.POST, request.FILES)
            if order_form.is_valid():
                try:
                    with transaction.atomic():
                        uploaded_file = request.FILES['archivo_libro']
                        fs = FileSystemStorage()
                        media_root = getattr(settings, "MEDIA_ROOT", None)
                        if not media_root: # Fallback for MEDIA_ROOT
                            media_root = os.path.join(settings.BASE_DIR, 'media_files')
                            if not os.path.exists(media_root):
                                os.makedirs(media_root, exist_ok=True)
                        order_files_dir = os.path.join(media_root, 'order_files')
                        if not os.path.exists(order_files_dir):
                            os.makedirs(order_files_dir, exist_ok=True)
                        relative_file_path = os.path.join('order_files', uploaded_file.name)
                        filename = fs.save(relative_file_path, uploaded_file)

                        nombre_cliente = order_form.cleaned_data['nombre_cliente']
                        cliente, created = Clientes.objects.get_or_create(nombre_cliente=nombre_cliente)

                        nueva_orden = OrdenesDeImpresion(
                            id_cliente=cliente,
                            fecha_entrega_solicitada=order_form.cleaned_data['fecha_entrega_solicitada'],
                            tipo_impresion=order_form.cleaned_data['tipo_impresion'],
                            cantidad_copias=order_form.cleaned_data['cantidad_copias'],
                            material_solicitado=order_form.cleaned_data.get('material_solicitado'),
                            archivo_adjunto_ruta=filename,
                            observaciones_cliente=order_form.cleaned_data.get('observaciones_cliente'),
                            estado_orden='pendiente'
                        )

                        numero_paginas_doc = order_form.cleaned_data['numero_paginas_documento']
                        cantidad_copias_orden = order_form.cleaned_data['cantidad_copias']
                        total_paginas_a_imprimir = numero_paginas_doc * cantidad_copias_orden
                        tipo_impresion_seleccionado = order_form.cleaned_data['tipo_impresion']

                        items_a_consumir_para_orden = []
                        items_a_consumir_para_orden.append({'id_db': ID_ITEM_PAPEL_DEFAULT, 'cantidad': total_paginas_a_imprimir, 'descripcion': 'Papel'})
                        if tipo_impresion_seleccionado == 'blanco-negro':
                            consumo_tinta_negra = total_paginas_a_imprimir * TINTA_POR_PAGINA_NEGRA
                            if consumo_tinta_negra > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_NEGRA, 'cantidad': consumo_tinta_negra, 'descripcion': 'Tinta Negra'})
                        elif tipo_impresion_seleccionado == 'color':
                            consumo_cyan = total_paginas_a_imprimir * TINTA_POR_PAGINA_COLOR_CHANNEL
                            consumo_magenta = total_paginas_a_imprimir * TINTA_POR_PAGINA_COLOR_CHANNEL
                            consumo_amarilla = total_paginas_a_imprimir * TINTA_POR_PAGINA_COLOR_CHANNEL
                            consumo_negra_color = total_paginas_a_imprimir * (TINTA_POR_PAGINA_COLOR_CHANNEL / 2)
                            if consumo_cyan > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_CYAN, 'cantidad': consumo_cyan, 'descripcion': 'Tinta Cyan'})
                            if consumo_magenta > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_MAGENTA, 'cantidad': consumo_magenta, 'descripcion': 'Tinta Magenta'})
                            if consumo_amarilla > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_AMARILLA, 'cantidad': consumo_amarilla, 'descripcion': 'Tinta Amarilla'})
                            if consumo_negra_color > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_NEGRA, 'cantidad': consumo_negra_color, 'descripcion': 'Tinta Negra (Color)'})

                        for item_info in items_a_consumir_para_orden:
                            item_inv = Items.objects.select_for_update().get(id_item=item_info['id_db'])
                            if item_inv.stock_actual is None or item_inv.stock_actual < item_info['cantidad']:
                                raise Exception(f"Stock insuficiente para {item_info['descripcion']} (ID: {item_info['id_db']}). Necesario: {item_info['cantidad']:.2f}, Disponible: {item_inv.stock_actual or 0}")
                            item_inv.stock_actual -= item_info['cantidad']
                            item_inv.save()

                        nueva_orden.save()

                        for item_info in items_a_consumir_para_orden:
                            OrdenInsumoConsumo.objects.create(
                                id_orden=nueva_orden,
                                id_item_id=item_info['id_db'],
                                cantidad_consumida=item_info['cantidad']
                            )

                        messages.success(request, f'Orden de impresión para {nombre_cliente} creada (ID: {nueva_orden.id_orden}) y stock actualizado.')
                        return redirect('gestion_impresion:primer_empleado_dashboard')
                except Items.DoesNotExist as e_item:
                     messages.error(request, f'Error al crear la orden: Item de inventario no encontrado - {e_item}')
                except Exception as e:
                    messages.error(request, f'Error al crear la orden y actualizar stock: {e}')
            else:
                messages.error(request, 'Por favor corrija los errores en el formulario de creación de orden.')

        elif 'submit_registrar_consumo' in request.POST:
            consumption_form = InsumoConsumptionForm(request.POST)
            if consumption_form.is_valid():
                try:
                    with transaction.atomic():
                        orden = consumption_form.cleaned_data['orden_consumo']
                        item_consumido_model = consumption_form.cleaned_data['item_consumido']
                        cantidad_consumida_manual = consumption_form.cleaned_data['cantidad_consumida']

                        item_inventario = Items.objects.select_for_update().get(id_item=item_consumido_model.id_item)

                        if item_inventario.stock_actual is None or item_inventario.stock_actual < cantidad_consumida_manual:
                            raise Exception(f"Stock insuficiente para {item_inventario.id_item}. Necesario: {cantidad_consumida_manual}, Disponible: {item_inventario.stock_actual or 0}")

                        item_inventario.stock_actual -= cantidad_consumida_manual
                        item_inventario.save()

                        OrdenInsumoConsumo.objects.create(
                            id_orden=orden,
                            id_item=item_consumido_model,
                            cantidad_consumida=cantidad_consumida_manual,
                        )
                        messages.success(request, f'Consumo de {cantidad_consumida_manual} unidad(es) de {item_consumido_model.id_item} registrado para la orden {orden.id_orden} y stock actualizado.')
                        return redirect('gestion_impresion:primer_empleado_dashboard')
                except Items.DoesNotExist:
                    messages.error(request, 'El item seleccionado para consumo no fue encontrado en el inventario.')
                except Exception as e:
                    messages.error(request, f'Error al registrar el consumo: {e}')
            else:
                messages.error(request, 'Por favor corrija los errores en el formulario de registro de consumo.')

    context = {
        'insumos': insumos_list,
        'order_form': order_form,
        'consumption_form': consumption_form,
        'all_orders_rf5': all_orders_rf5,
        'selected_order_details_rf5': selected_order_details_rf5,
        'selected_orden_id_rf5_val': selected_orden_id_rf5_val_str # Pass the string version back for select option matching
    }
    return render(request, 'gestion_impresion/primer_empleado_dashboard.html', context)

def segundo_empleado_dashboard_view(request):
    context = {}
    return render(request, 'gestion_impresion/segundo_empleado_dashboard.html', context)
