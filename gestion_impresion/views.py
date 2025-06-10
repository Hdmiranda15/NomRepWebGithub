from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone # For updating 'ultima_actualizacion_estado'

# Para procesar documentos (DOCX/DOC a PDF y contar páginas)
import subprocess
from pypdf import PdfReader # Asegúrate de que 'pypdf' esté en tu requirements.txt

# Importar todos los modelos necesarios
from .models import (
    Items, DescripcionesMaterial, Clientes, OrdenesDeImpresion,
    OrdenInsumoConsumo, Impresoras, Proveedores, Aplicaciones,
    ItemProveedor, ItemAplicacion # Asegúrate de importar todos si los vas a usar en otras vistas o en el admin
)

# Importar todos los formularios necesarios
from .forms import (
    OrderCreationForm, InsumoConsumptionForm, OrderUpdateForm,
    AssignPrinterToOrderForm, UpdatePrinterStatusForm
)

# --- Constantes de Consumo de Insumos (pueden ser configurables en la DB en un sistema más grande) ---
ID_ITEM_PAPEL_DEFAULT = 'S-OFF-P-BOND-090'
ID_ITEM_TINTA_NEGRA = 'T-OFF-CMYK-K'
ID_ITEM_TINTA_CYAN = 'T-OFF-CMYK-C'
ID_ITEM_TINTA_MAGENTA = 'T-OFF-CMYK-M'
ID_ITEM_TINTA_AMARILLA = 'T-OFF-CMYK-Y'

# Tasas de consumo por página (ejemplos, ajusta según la realidad)
# Por ejemplo, 0.02 unidades de tinta negra por página
TINTA_POR_PAGINA_NEGRA = 0.02
# Para color, consumo por cada canal (Cyan, Magenta, Amarillo)
TINTA_POR_PAGINA_COLOR_CHANNEL = 0.01

# --- Vista para el Dashboard del Primer Empleado ---
def primer_empleado_dashboard_view(request):
    # Inicializar formularios para el contexto GET
    order_form = OrderCreationForm()
    consumption_form = InsumoConsumptionForm()
    order_update_form = OrderUpdateForm()
    order_to_update_instance = None # Para precargar el formulario de actualización

    # Datos para la sección "Consultar Insumos" (RF4)
    insumos_list = Items.objects.select_related('descripcion_especifica').all()

    # Lógica para la sección "Ver Estado Orden" (RF5)
    # Lista todas las órdenes, incluyendo cliente y posible impresora asignada, ordenadas por fecha
    all_orders_rf5 = OrdenesDeImpresion.objects.select_related('id_cliente', 'id_impresora_asignada').order_by('-fecha_creacion_orden')
    selected_order_details_rf5 = None
    selected_orden_id_rf5_val_str = request.GET.get('selected_orden_id_rf5') # Obtener ID de la URL
    if selected_orden_id_rf5_val_str:
        try:
            selected_orden_id_rf5_int = int(selected_orden_id_rf5_val_str)
            selected_order_details_rf5 = OrdenesDeImpresion.objects.select_related('id_cliente', 'id_impresora_asignada').get(id_orden=selected_orden_id_rf5_int)
        except (OrdenesDeImpresion.DoesNotExist, ValueError):
            messages.error(request, f"La orden con ID '{selected_orden_id_rf5_val_str}' para visualización no fue encontrada o el ID no es válido.")
            selected_orden_id_rf5_val_str = None # Limpiar para no mostrar la orden anterior

    # Lógica para la sección "Actualizar Orden" (RF6)
    # Reutiliza all_orders_rf5 para la lista de selección
    update_orden_id_get_val_str = request.GET.get('update_orden_id') # Obtener ID de la URL
    if update_orden_id_get_val_str and not request.POST: # Si se selecciona una orden vía GET y no es un POST de actualización
        try:
            update_orden_id_get_int = int(update_orden_id_get_val_str)
            order_to_update_instance = get_object_or_404(OrdenesDeImpresion, id_orden=update_orden_id_get_int)
            order_update_form = OrderUpdateForm(instance=order_to_update_instance) # Precargar el formulario con los datos de la orden
        except (ValueError, OrdenesDeImpresion.DoesNotExist):
            messages.error(request, f"El ID de orden proporcionado para actualizar ('{update_orden_id_get_val_str}') no es válido o no existe.")
            update_orden_id_get_val_str = None # Limpiar para no precargar nada

    # --- Manejo de Solicitudes POST (Envío de Formularios) ---
    if request.method == 'POST':
        # --- Lógica para Crear Orden (RF1) ---
        if 'submit_crear_orden' in request.POST:
            order_form = OrderCreationForm(request.POST, request.FILES)
            if order_form.is_valid():
                try:
                    with transaction.atomic(): # Asegura que todas las operaciones se completen o ninguna
                        uploaded_file = request.FILES['archivo_libro']
                        
                        # Validar extensión del archivo
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        if file_ext not in ['.docx', '.doc', '.pdf']:
                            messages.error(request, "Solo se permiten archivos .docx, .doc o .pdf para la subida.")
                            return redirect('gestion_impresion:primer_empleado_dashboard')

                        # Configurar rutas de almacenamiento de archivos
                        fs = FileSystemStorage()
                        media_root = getattr(settings, "MEDIA_ROOT", None)
                        if not media_root: # Fallback si MEDIA_ROOT no está explícitamente definido
                            media_root = os.path.join(settings.BASE_DIR, 'media_files')
                            if not os.path.exists(media_root):
                                os.makedirs(media_root, exist_ok=True)

                        order_files_dir = os.path.join(media_root, 'order_files')
                        if not os.path.exists(order_files_dir):
                            os.makedirs(order_files_dir, exist_ok=True)

                        # Guardar el archivo original en la ruta de media
                        original_file_path = os.path.join(order_files_dir, uploaded_file.name)
                        fs.save(original_file_path, uploaded_file) # Esto guarda el archivo físico

                        num_pages_found = 0 # Inicializar el contador de páginas

                        # --- Lógica para contar páginas según el tipo de archivo ---
                        if file_ext == '.pdf':
                            try:
                                with open(original_file_path, 'rb') as pdf_file_obj:
                                    pdf_reader = PdfReader(pdf_file_obj)
                                    num_pages_found = len(pdf_reader.pages)
                                messages.info(request, f"Documento PDF procesado. Páginas detectadas: {num_pages_found}.")
                            except Exception as e:
                                messages.error(request, f"Error al leer el archivo PDF: {e}. Asegúrese que el PDF no está corrupto.")
                                os.remove(original_file_path) # Limpiar archivo subido
                                return redirect('gestion_impresion:primer_empleado_dashboard')
                        elif file_ext in ['.docx', '.doc']:
                            # Preparar la ruta para el PDF temporal
                            pdf_temp_path = original_file_path.rsplit('.', 1)[0] + '.pdf'
                            try:
                                # Convertir DOCX/DOC a PDF usando unoconv
                                # 'check=True' asegura que se lance un CalledProcessError si el comando falla
                                subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_temp_path, original_file_path], check=True)

                                # Leer el PDF temporal y obtener el número de páginas
                                with open(pdf_temp_path, 'rb') as pdf_file_obj:
                                    pdf_reader = PdfReader(pdf_file_obj)
                                    num_pages_found = len(pdf_reader.pages)

                                messages.info(request, f"Documento {file_ext} procesado. Páginas detectadas: {num_pages_found}.")

                            except FileNotFoundError:
                                messages.error(request, "La herramienta 'unoconv' o 'libreoffice' no está instalada o no se encuentra en el PATH del sistema. Por favor, asegúrese de instalarla (ej: sudo apt install libreoffice unoconv).")
                                os.remove(original_file_path) # Limpiar archivo subido
                                return redirect('gestion_impresion:primer_empleado_dashboard')
                            except subprocess.CalledProcessError as e:
                                messages.error(request, f"Error al convertir el documento a PDF: {e}. Asegúrese que el archivo {file_ext} es válido.")
                                os.remove(original_file_path)
                                if os.path.exists(pdf_temp_path): os.remove(pdf_temp_path) # Limpiar PDF temporal si se creó corrupto
                                return redirect('gestion_impresion:primer_empleado_dashboard')
                            except Exception as e: # Captura otros errores inesperados durante la conversión/lectura
                                messages.error(request, f"Ocurrió un error inesperado al procesar el documento: {e}")
                                os.remove(original_file_path)
                                if os.path.exists(pdf_temp_path): os.remove(pdf_temp_path)
                                return redirect('gestion_impresion:primer_empleado_dashboard')
                            finally:
                                # Asegurar que el archivo PDF temporal se elimine siempre
                                if os.path.exists(pdf_temp_path):
                                    os.remove(pdf_temp_path)
                        else:
                            messages.error(request, "Tipo de archivo no soportado para el conteo de páginas.")
                            os.remove(original_file_path)
                            return redirect('gestion_impresion:primer_empleado_dashboard')

                        # Crear o obtener el cliente
                        nombre_cliente = order_form.cleaned_data['nombre_cliente']
                        cliente, created = Clientes.objects.get_or_create(nombre_cliente=nombre_cliente)

                        # Crear la nueva orden de impresión
                        nueva_orden = OrdenesDeImpresion(
                            id_cliente=cliente,
                            fecha_entrega_solicitada=order_form.cleaned_data['fecha_entrega_solicitada'],
                            tipo_impresion=order_form.cleaned_data['tipo_impresion'],
                            cantidad_copias=order_form.cleaned_data['cantidad_copias'],
                            # Guardar el número de páginas detectado (no el del formulario si existía)
                            numero_paginas_documento_ingresado=num_pages_found,
                            material_solicitado=order_form.cleaned_data.get('material_solicitado'),
                            # Guardar la ruta relativa del archivo original (DOCX o PDF)
                            archivo_adjunto_ruta=os.path.relpath(original_file_path, media_root),
                            observaciones_cliente=order_form.cleaned_data.get('observaciones_cliente'),
                            estado_orden='pendiente' # Estado inicial de la orden
                        )

                        # --- Cálculo y Actualización de Stock de Insumos (RF2) ---
                        total_paginas_a_imprimir = num_pages_found * order_form.cleaned_data['cantidad_copias']
                        tipo_impresion_seleccionado = order_form.cleaned_data['tipo_impresion']

                        items_a_consumir_para_orden = []
                        # Siempre se considera papel
                        items_a_consumir_para_orden.append({'id_db': ID_ITEM_PAPEL_DEFAULT, 'cantidad': total_paginas_a_imprimir, 'descripcion': 'Papel'})

                        # Consumo de tinta según el tipo de impresión
                        if tipo_impresion_seleccionado == 'blanco-negro':
                            consumo_tinta_negra = total_paginas_a_imprimir * TINTA_POR_PAGINA_NEGRA
                            if consumo_tinta_negra > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_NEGRA, 'cantidad': consumo_tinta_negra, 'descripcion': 'Tinta Negra'})
                        elif tipo_impresion_seleccionado == 'color':
                            consumo_cyan = total_paginas_a_imprimir * TINTA_POR_PAGINA_COLOR_CHANNEL
                            consumo_magenta = total_paginas_a_imprimir * TINTA_POR_PAGINA_COLOR_CHANNEL
                            consumo_amarilla = total_paginas_a_imprimir * TINTA_POR_PAGINA_COLOR_CHANNEL
                            # Asumimos que algo de tinta negra también se usa en impresiones a color
                            consumo_negra_color = total_paginas_a_imprimir * (TINTA_POR_PAGINA_COLOR_CHANNEL / 2)
                            if consumo_cyan > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_CYAN, 'cantidad': consumo_cyan, 'descripcion': 'Tinta Cyan'})
                            if consumo_magenta > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_MAGENTA, 'cantidad': consumo_magenta, 'descripcion': 'Tinta Magenta'})
                            if consumo_amarilla > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_AMARILLA, 'cantidad': consumo_amarilla, 'descripcion': 'Tinta Amarilla'})
                            if consumo_negra_color > 0: items_a_consumir_para_orden.append({'id_db': ID_ITEM_TINTA_NEGRA, 'cantidad': consumo_negra_color, 'descripcion': 'Tinta Negra (Color)'})

                        # Actualizar el stock de cada item en la base de datos
                        for item_info in items_a_consumir_para_orden:
                            # select_for_update() bloquea la fila para evitar condiciones de carrera en un entorno multiusuario
                            item_inv = Items.objects.select_for_update().get(id_item=item_info['id_db'])
                            if item_inv.stock_actual is None or item_inv.stock_actual < item_info['cantidad']:
                                # Si el stock es insuficiente, se lanza una excepción y se hace rollback de la transacción
                                if os.path.exists(original_file_path):
                                    os.remove(original_file_path) # Limpiar archivo subido si falla el stock
                                raise Exception(f"Stock insuficiente para {item_info['descripcion']} (ID: {item_info['id_db']}). Necesario: {item_info['cantidad']:.2f}, Disponible: {item_inv.stock_actual or 0}")
                            item_inv.stock_actual -= item_info['cantidad']
                            item_inv.save()

                        # Guardar la orden si el stock es suficiente
                        nueva_orden.save()

                        # Registrar el consumo de insumos asociado a la orden (RF2)
                        for item_info in items_a_consumir_para_orden:
                            OrdenInsumoConsumo.objects.create(
                                id_orden=nueva_orden,
                                id_item_id=item_info['id_db'], # Usar id_item_id si id_item es el campo FK
                                cantidad_consumida=item_info['cantidad']
                            )

                        messages.success(request, f'Orden de impresión para {nombre_cliente} creada (ID: {nueva_orden.id_orden}) y stock actualizado.')
                        # Redirigir para limpiar el formulario y evitar reenvíos
                        return redirect('gestion_impresion:primer_empleado_dashboard')

                except Items.DoesNotExist as e_item:
                    messages.error(request, f'Error al crear la orden: Item de inventario no encontrado - {e_item}. Verifique los ID de los items constantes.')
                except Exception as e:
                    messages.error(request, f'Error general al crear la orden y actualizar stock: {e}')
            else:
                messages.error(request, 'Por favor corrija los errores en el formulario de creación de orden.')

        # --- Lógica para Registrar Consumo de Insumos (RF3) ---
        elif 'submit_registrar_consumo' in request.POST:
            consumption_form = InsumoConsumptionForm(request.POST)
            if consumption_form.is_valid():
                try:
                    with transaction.atomic():
                        orden = consumption_form.cleaned_data['orden_consumo']
                        item_consumido_model = consumption_form.cleaned_data['item_consumido']
                        cantidad_consumida_manual = consumption_form.cleaned_data['cantidad_consumida']

                        # Bloquear y obtener el item de inventario
                        item_inventario = Items.objects.select_for_update().get(id_item=item_consumido_model.id_item)

                        # Verificar stock
                        if item_inventario.stock_actual is None or item_inventario.stock_actual < cantidad_consumida_manual:
                            raise Exception(f"Stock insuficiente para {item_inventario.id_item}. Necesario: {cantidad_consumida_manual}, Disponible: {item_inventario.stock_actual or 0}")

                        # Actualizar stock
                        item_inventario.stock_actual -= cantidad_consumida_manual
                        item_inventario.save()

                        # Registrar el consumo
                        OrdenInsumoConsumo.objects.create(
                            id_orden=orden,
                            id_item=item_consumido_model,
                            cantidad_consumida=cantidad_consumida_manual,
                        )
                        messages.success(request, f'Consumo de {cantidad_consumida_manual} unidad(es) de {item_consumido_model.id_item} registrado para la orden {orden.id_orden} y stock actualizado.')
                        # Redirigir para limpiar el formulario
                        return redirect('gestion_impresion:primer_empleado_dashboard')
                except Items.DoesNotExist:
                    messages.error(request, 'El item seleccionado para consumo no fue encontrado en el inventario.')
                except Exception as e:
                    messages.error(request, f'Error al registrar el consumo: {e}')
            else:
                messages.error(request, 'Por favor corrija los errores en el formulario de registro de consumo.')

        # --- Lógica para Actualizar Orden (RF6) ---
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
                        order_update_form.save() # Guarda los cambios al modelo de la orden
                        messages.success(request, f"Orden #{order_to_update_instance.id_orden} actualizada exitosamente.")
                        # Redirigir manteniendo la orden seleccionada para que el usuario vea los cambios
                        return redirect(f"{request.path}?update_orden_id={order_to_update_instance.id_orden}")
                else:
                    messages.error(request, f"Por favor corrija los errores en el formulario de actualización de orden para la Orden #{order_to_update_instance.id_orden}.")
                    # Es importante que el contexto de la vista se mantenga para mostrar los errores del formulario
                    # Re-establecer update_orden_id_get_val_str para que el template sepa qué orden intentaba actualizar
                    update_orden_id_get_val_str = str(order_to_update_instance.id_orden)
            except ValueError:
                messages.error(request, f"El ID de orden proporcionado para actualizar ('{orden_id_to_update_post_str}') no es válido.")
            except OrdenesDeImpresion.DoesNotExist:
                messages.error(request, f"La orden con ID '{orden_id_to_update_post_str}' para actualizar no fue encontrada.")

    # --- Contexto para el Template del Primer Empleado ---
    context = {
        'insumos': insumos_list,
        'order_form': order_form, # Se envía la instancia del formulario, sea vacía o con errores
        'consumption_form': consumption_form, # Se envía la instancia del formulario
        'all_orders_rf5': all_orders_rf5, # Todas las órdenes para la lista de "Ver Estado"
        'selected_order_details_rf5': selected_order_details_rf5, # Detalles de la orden seleccionada para RF5
        'selected_orden_id_rf5_val': selected_orden_id_rf5_val_str, # ID de la orden seleccionada para mantener el <select>
        'all_orders_rf6': all_orders_rf5, # Reutiliza la misma lista para la selección de "Actualizar Orden"
        'order_update_form': order_update_form, # Formulario de actualización (puede estar precargado o vacío)
        'order_to_update_instance': order_to_update_instance, # Instancia de la orden si se está actualizando (para mostrar detalles)
        'update_orden_id_val': update_orden_id_get_val_str # ID para mantener el <select> en "Actualizar Orden"
    }
    return render(request, 'gestion_impresion/primer_empleado_dashboard.html', context)


# --- Vista para el Dashboard del Segundo Empleado ---
def segundo_empleado_dashboard_view(request):
    # Inicializar formularios para el contexto GET
    assign_printer_form = AssignPrinterToOrderForm()
    update_printer_status_form = UpdatePrinterStatusForm()

    # Manejo de Solicitudes POST para este dashboard
    if request.method == 'POST':
        # --- Lógica para Asignar Impresora a Orden (RF9) ---
        if 'submit_assign_printer' in request.POST:
            assign_printer_form = AssignPrinterToOrderForm(request.POST)
            if assign_printer_form.is_valid():
                try:
                    with transaction.atomic():
                        orden = assign_printer_form.cleaned_data['orden_a_asignar']
                        impresora = assign_printer_form.cleaned_data['impresora_disponible']

                        # Obtener instancias de la DB y bloquearlas para actualización
                        orden_to_update = OrdenesDeImpresion.objects.select_for_update().get(pk=orden.pk)
                        impresora_to_update = Impresoras.objects.select_for_update().get(pk=impresora.pk)

                        # Validaciones adicionales
                        if impresora_to_update.estado_impresora != 'disponible':
                            messages.error(request, f"La impresora '{impresora_to_update.nombre_impresora}' ya no está disponible para asignación. Su estado actual es '{impresora_to_update.estado_impresora}'.")
                        elif orden_to_update.estado_orden not in ['pendiente', 'en_pausa']:
                            messages.error(request, f"La orden '{orden_to_update.id_orden}' no está en un estado asignable (actual: {orden_to_update.estado_orden}). Solo 'pendiente' o 'en_pausa'.")
                        else:
                            # Asignar impresora a la orden y actualizar estado de la orden
                            orden_to_update.id_impresora_asignada = impresora_to_update
                            orden_to_update.estado_orden = 'en_proceso' # Cambiar estado de la orden
                            orden_to_update.save()

                            # Actualizar estado de la impresora
                            impresora_to_update.estado_impresora = 'ocupada'
                            impresora_to_update.ultima_actualizacion_estado = timezone.now()
                            impresora_to_update.save()

                            messages.success(request, f"Impresora '{impresora_to_update.nombre_impresora}' asignada a la orden #{orden_to_update.id_orden}. Estado de orden actualizado a '{orden_to_update.estado_orden}'.")
                            # Reiniciar formularios para limpiar campos después de un éxito
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

        # --- Lógica para Actualizar Estado de Impresora (RF11) ---
        elif 'submit_update_printer_status' in request.POST:
            update_printer_status_form = UpdatePrinterStatusForm(request.POST)
            if update_printer_status_form.is_valid():
                try:
                    with transaction.atomic():
                        impresora = update_printer_status_form.cleaned_data['impresora_a_actualizar']
                        nuevo_estado = update_printer_status_form.cleaned_data['nuevo_estado_impresora']

                        # Bloquear y obtener la impresora
                        impresora_to_update = Impresoras.objects.select_for_update().get(pk=impresora.pk)

                        # Actualizar estado de la impresora
                        impresora_to_update.estado_impresora = nuevo_estado
                        impresora_to_update.ultima_actualizacion_estado = timezone.now()
                        impresora_to_update.save()

                        messages.success(request, f"Estado de la impresora '{impresora_to_update.nombre_impresora}' actualizado a '{nuevo_estado}'.")
                        # Reiniciar formularios para limpiar campos después de un éxito
                        update_printer_status_form = UpdatePrinterStatusForm()
                        assign_printer_form = AssignPrinterToOrderForm() # También el otro por si su queryset cambió
                except Impresoras.DoesNotExist:
                    messages.error(request, "La impresora seleccionada para actualizar ya no existe.")
                except Exception as e:
                    messages.error(request, f"Error al actualizar estado de impresora: {e}")
            else:
                messages.error(request, "Por favor corrija los errores en el formulario de actualización de estado de impresora.")

    # --- Contexto para el Template del Segundo Empleado ---

    # Para RF8: Ver Estado de Orden (versión del empleado de producción)
    # Filtra órdenes relevantes (pendientes, en proceso, en pausa) para que el empleado se enfoque en su trabajo.
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
            # Evitar mensajes de error duplicados si ya se generó uno por POST
            if not any(m.level == messages.ERROR for m in messages.get_messages(request)):
                 messages.error(request, f"La orden con ID '{selected_orden_id_rf8_val_str}' no fue encontrada o el ID es inválido.")
            selected_order_details_rf8 = None
            selected_orden_id_rf8_val_str = None # Limpiar el valor para el select

    # Para RF10: Consultar Disponibilidad de Impresoras
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
