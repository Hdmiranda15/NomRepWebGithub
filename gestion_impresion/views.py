from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone # For updating 'ultima_actualizacion_estado'

# Ensure all necessary models and forms are imported
from .models import Items, DescripcionesMaterial, Clientes, OrdenesDeImpresion, OrdenInsumoConsumo, Impresoras
from .forms import OrderCreationForm, InsumoConsumptionForm, OrderUpdateForm, AssignPrinterToOrderForm, UpdatePrinterStatusForm

# Placeholder Item IDs and Consumption Rates
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
    order_update_form = OrderUpdateForm()
    order_to_update_instance = None

    all_orders_rf5 = OrdenesDeImpresion.objects.select_related('id_cliente').order_by('-fecha_creacion_orden')
    selected_order_details_rf5 = None
    selected_orden_id_rf5_val_str = request.GET.get('selected_orden_id_rf5')
    if selected_orden_id_rf5_val_str:
        try:
            selected_orden_id_rf5_int = int(selected_orden_id_rf5_val_str)
            selected_order_details_rf5 = OrdenesDeImpresion.objects.select_related('id_cliente', 'id_impresora_asignada').get(id_orden=selected_orden_id_rf5_int)
        except (OrdenesDeImpresion.DoesNotExist, ValueError):
            messages.error(request, f"La orden con ID '{selected_orden_id_rf5_val_str}' para visualización no fue encontrada o el ID no es válido.")
            selected_orden_id_rf5_val_str = None

    update_orden_id_get_val_str = request.GET.get('update_orden_id')
    if update_orden_id_get_val_str and not request.POST:
        try:
            update_orden_id_get_int = int(update_orden_id_get_val_str)
            order_to_update_instance = get_object_or_404(OrdenesDeImpresion, id_orden=update_orden_id_get_int)
            order_update_form = OrderUpdateForm(instance=order_to_update_instance)
        except (ValueError, OrdenesDeImpresion.DoesNotExist):
             messages.error(request, f"El ID de orden proporcionado para actualizar ('{update_orden_id_get_val_str}') no es válido o no existe.")
             update_orden_id_get_val_str = None

    if request.method == 'POST':
        if 'submit_crear_orden' in request.POST:
            order_form = OrderCreationForm(request.POST, request.FILES)
            if order_form.is_valid():
                try:
                    with transaction.atomic():
                        uploaded_file = request.FILES['archivo_libro']
                        fs = FileSystemStorage()
                        media_root = getattr(settings, "MEDIA_ROOT", None)
                        if not media_root:
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
                            numero_paginas_documento_ingresado=order_form.cleaned_data.get('numero_paginas_documento'), # Save the new field
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

        elif 'submit_actualizar_orden' in request.POST:
            orden_id_to_update_post_str = request.POST.get('orden_id_to_update')
            if not orden_id_to_update_post_str:
                messages.error(request, "No se especificó el ID de la orden para actualizar.")
                return redirect('gestion_impresion:primer_empleado_dashboard')

            try:
                orden_id_to_update_post_int = int(orden_id_to_update_post_str)
                order_to_update_instance = get_object_or_404(OrdenesDeImpresion, id_orden=orden_id_to_update_post_int)
                order_update_form = OrderUpdateForm(request.POST, instance=order_to_update_instance)

                if order_update_form.is_valid():
                    with transaction.atomic():
                        order_update_form.save()
                        messages.success(request, f"Orden #{order_to_update_instance.id_orden} actualizada exitosamente.")
                        return redirect(f"{request.path}?update_orden_id={order_to_update_instance.id_orden}")
                else:
                    messages.error(request, f"Por favor corrija los errores en el formulario de actualización de orden para la Orden #{order_to_update_instance.id_orden}.")
                    update_orden_id_get_val_str = str(order_to_update_instance.id_orden)
            except ValueError:
                messages.error(request, f"El ID de orden proporcionado para actualizar ('{orden_id_to_update_post_str}') no es válido.")
            except OrdenesDeImpresion.DoesNotExist:
                messages.error(request, f"La orden con ID '{orden_id_to_update_post_str}' para actualizar no fue encontrada.")

    context = {
        'insumos': insumos_list,
        'order_form': order_form,
        'consumption_form': consumption_form,
        'all_orders_rf5': all_orders_rf5,
        'selected_order_details_rf5': selected_order_details_rf5,
        'selected_orden_id_rf5_val': selected_orden_id_rf5_val_str,
        'all_orders_rf6': all_orders_rf5,
        'order_update_form': order_update_form,
        'order_to_update_instance': order_to_update_instance,
        'update_orden_id_val': update_orden_id_get_val_str
    }
    return render(request, 'gestion_impresion/primer_empleado_dashboard.html', context)


def segundo_empleado_dashboard_view(request):
    assign_printer_form = AssignPrinterToOrderForm()
    update_printer_status_form = UpdatePrinterStatusForm()

    if request.method == 'POST':
        if 'submit_assign_printer' in request.POST:
            assign_printer_form = AssignPrinterToOrderForm(request.POST)
            if assign_printer_form.is_valid():
                try:
                    with transaction.atomic():
                        orden = assign_printer_form.cleaned_data['orden_a_asignar']
                        impresora = assign_printer_form.cleaned_data['impresora_disponible']

                        orden_to_update = OrdenesDeImpresion.objects.select_for_update().get(pk=orden.pk)
                        impresora_to_update = Impresoras.objects.select_for_update().get(pk=impresora.pk)

                        if impresora_to_update.estado_impresora != 'disponible':
                            messages.error(request, f"La impresora '{impresora_to_update.nombre_impresora}' ya no está disponible.")
                        elif orden_to_update.estado_orden not in ['pendiente', 'en_pausa']:
                             messages.error(request, f"La orden '{orden_to_update.id_orden}' no está en un estado asignable (actual: {orden_to_update.estado_orden}).")
                        else:
                            orden_to_update.id_impresora_asignada = impresora_to_update
                            orden_to_update.estado_orden = 'en_proceso'
                            orden_to_update.save()

                            impresora_to_update.estado_impresora = 'ocupada'
                            impresora_to_update.ultima_actualizacion_estado = timezone.now()
                            impresora_to_update.save()

                            messages.success(request, f"Impresora '{impresora_to_update.nombre_impresora}' asignada a la orden #{orden_to_update.id_orden}. Estado de orden actualizado a '{orden_to_update.estado_orden}'.")
                            assign_printer_form = AssignPrinterToOrderForm()
                            update_printer_status_form = UpdatePrinterStatusForm()
                except OrdenesDeImpresion.DoesNotExist:
                    messages.error(request, "La orden seleccionada para asignar ya no existe.")
                except Impresoras.DoesNotExist:
                    messages.error(request, "La impresora seleccionada para asignar ya no existe.")
                except Exception as e:
                    messages.error(request, f"Error al asignar impresora: {e}")
            else:
                messages.error(request, "Por favor corrija los errores en el formulario de asignación de impresora.")

        elif 'submit_update_printer_status' in request.POST:
            update_printer_status_form = UpdatePrinterStatusForm(request.POST)
            if update_printer_status_form.is_valid():
                try:
                    with transaction.atomic():
                        impresora = update_printer_status_form.cleaned_data['impresora_a_actualizar']
                        nuevo_estado = update_printer_status_form.cleaned_data['nuevo_estado_impresora']

                        impresora_to_update = Impresoras.objects.select_for_update().get(pk=impresora.pk)

                        impresora_to_update.estado_impresora = nuevo_estado
                        impresora_to_update.ultima_actualizacion_estado = timezone.now()
                        impresora_to_update.save()

                        messages.success(request, f"Estado de la impresora '{impresora_to_update.nombre_impresora}' actualizado a '{nuevo_estado}'.")
                        update_printer_status_form = UpdatePrinterStatusForm()
                        assign_printer_form = AssignPrinterToOrderForm()
                except Impresoras.DoesNotExist:
                     messages.error(request, "La impresora seleccionada para actualizar ya no existe.")
                except Exception as e:
                    messages.error(request, f"Error al actualizar estado de impresora: {e}")
            else:
                messages.error(request, "Por favor corrija los errores en el formulario de actualización de estado de impresora.")

    orders_for_rf8 = OrdenesDeImpresion.objects.select_related('id_cliente').exclude(
        estado_orden__in=['completada', 'cancelada']
    ).order_by('fecha_creacion_orden')

    selected_order_details_rf8 = None
    selected_orden_id_rf8_val_str = request.GET.get('selected_orden_id_rf8')
    if selected_orden_id_rf8_val_str:
        try:
            selected_orden_id_rf8_int = int(selected_orden_id_rf8_val_str)
            selected_order_details_rf8 = OrdenesDeImpresion.objects.select_related(
                'id_cliente', 'id_impresora_asignada'
            ).get(id_orden=selected_orden_id_rf8_int)
        except (OrdenesDeImpresion.DoesNotExist, ValueError):
            if not any(m.level == messages.ERROR for m in messages.get_messages(request)):
                 messages.error(request, f"La orden con ID '{selected_orden_id_rf8_val_str}' no fue encontrada o el ID es inválido.")
            selected_order_details_rf8 = None
            selected_orden_id_rf8_val_str = None

    all_printers_rf10 = Impresoras.objects.all().order_by('nombre_impresora')

    context = {
        'all_orders_rf8': orders_for_rf8,
        'selected_order_details_rf8': selected_order_details_rf8,
        'selected_orden_id_rf8_val': selected_orden_id_rf8_val_str,
        'all_printers_rf10': all_printers_rf10,
        'assign_printer_form': assign_printer_form,
        'update_printer_status_form': update_printer_status_form,
    }
    return render(request, 'gestion_impresion/segundo_empleado_dashboard.html', context)
