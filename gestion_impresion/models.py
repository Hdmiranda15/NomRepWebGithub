from django.db import models

class DescripcionesMaterial(models.Model):
    descripcion_especifica = models.TextField(primary_key=True)
    tecnologia = models.TextField(blank=True, null=True)
    tipo_sustrato_principal = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'descripciones_material'

class Items(models.Model):
    id_item = models.TextField(primary_key=True)
    # Django typically creates an 'id' field automatically if no primary_key is specified.
    # Since id_item is the PK, ensure it's correctly defined.
    # If 'descripcion_especifica' is a ForeignKey in the DB, it should be:
    # descripcion_especifica = models.ForeignKey(DescripcionesMaterial, models.DO_NOTHING, db_column='descripcion_especifica', blank=True, null=True)
    # However, based on your DDL, it seems to be just a text field that matches.
    # For unmanaged models, keeping it simple is often best if Django isn't managing relations.
    descripcion_especifica = models.ForeignKey(DescripcionesMaterial, models.DO_NOTHING, db_column='descripcion_especifica')
    especificacion_tecnica = models.TextField(blank=True, null=True)
    formato_presentacion = models.TextField(blank=True, null=True)
    unidad_medida_inventario = models.TextField(blank=True, null=True)
    stock_actual = models.IntegerField(blank=True, null=True)
    stock_minimo_pedido = models.TextField(blank=True, null=True) # Assuming text, adjust if numeric

    class Meta:
        managed = False
        db_table = 'items'

class Proveedores(models.Model):
    id_proveedor = models.AutoField(primary_key=True) # SERIAL maps to AutoField
    nombre_proveedor = models.TextField()

    class Meta:
        managed = False
        db_table = 'proveedores'

class Aplicaciones(models.Model):
    id_aplicacion = models.AutoField(primary_key=True) # SERIAL maps to AutoField
    nombre_aplicacion = models.TextField()

    class Meta:
        managed = False
        db_table = 'aplicaciones'

class ItemProveedor(models.Model):
    # For composite keys, Django's ORM handles them but requires one field to be primary_key=True
    # or define a unique_together in Meta. For unmanaged, often defining them as individual fields is enough
    # if you're mostly reading. If writing through ORM, more care is needed.
    # Let's assume id_item_proveedor as a unique identifier for Django if inserts are needed,
    # or handle composite PKs carefully. For now, a simple representation:
    id_item_proveedor = models.AutoField(primary_key=True) # Surrogate key for Django ORM if needed for admin, etc.
    id_item = models.ForeignKey(Items, models.DO_NOTHING, db_column='id_item')
    id_proveedor = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='id_proveedor')
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # NUMERIC maps to DecimalField

    class Meta:
        managed = False
        db_table = 'item_proveedor'
        unique_together = (('id_item', 'id_proveedor'),) # Reflects DB composite PK

class ItemAplicacion(models.Model):
    id_item_aplicacion = models.AutoField(primary_key=True) # Surrogate key
    id_item = models.ForeignKey(Items, models.DO_NOTHING, db_column='id_item')
    id_aplicacion = models.ForeignKey(Aplicaciones, models.DO_NOTHING, db_column='id_aplicacion')

    class Meta:
        managed = False
        db_table = 'item_aplicacion'
        unique_together = (('id_item', 'id_aplicacion'),)

# New models (add these below existing models in gestion_impresion/models.py)

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre_cliente = models.TextField()
    contacto_email = models.TextField(blank=True, null=True)
    contacto_telefono = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True) # Default is handled by DB

    class Meta:
        managed = False
        db_table = 'clientes'

class Impresoras(models.Model):
    id_impresora = models.AutoField(primary_key=True)
    nombre_impresora = models.TextField(unique=True)
    modelo_impresora = models.TextField(blank=True, null=True)
    tipo_impresora = models.TextField(blank=True, null=True)
    estado_impresora = models.TextField() # Default is handled by DB
    ubicacion = models.TextField(blank=True, null=True)
    ultima_actualizacion_estado = models.DateTimeField(blank=True, null=True) # Default is handled by DB

    class Meta:
        managed = False
        db_table = 'impresoras'

class OrdenesDeImpresion(models.Model):
    id_orden = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente')
    fecha_creacion_orden = models.DateTimeField(blank=True, null=True) # Default is handled by DB
    fecha_entrega_solicitada = models.DateField()
    fecha_entrega_estimada = models.DateField(blank=True, null=True)
    tipo_impresion = models.TextField()
    cantidad_copias = models.IntegerField()
    material_solicitado = models.TextField(blank=True, null=True)
    archivo_adjunto_ruta = models.TextField(blank=True, null=True)
    observaciones_cliente = models.TextField(blank=True, null=True)
    estado_orden = models.TextField() # Default is handled by DB
    id_impresora_asignada = models.ForeignKey(Impresoras, models.DO_NOTHING, db_column='id_impresora_asignada', blank=True, null=True)
    costo_total_estimado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    costo_total_final = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    prioridad = models.IntegerField(blank=True, null=True) # Default is handled by DB

    class Meta:
        managed = False
        db_table = 'ordenesdeimpresion' # Django defaults to lowercase

class OrdenInsumoConsumo(models.Model):
    id_orden_insumo_consumo = models.AutoField(primary_key=True)
    id_orden = models.ForeignKey(OrdenesDeImpresion, models.DO_NOTHING, db_column='id_orden')
    # Assuming 'Items' model is already defined above in the same file
    id_item = models.ForeignKey('Items', models.DO_NOTHING, db_column='id_item')
    cantidad_consumida = models.IntegerField()
    fecha_consumo = models.DateTimeField(blank=True, null=True) # Default is handled by DB
    registrado_por_empleado_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ordeninsumoconsumo' # Django defaults to lowercase
        unique_together = (('id_orden', 'id_item'),)
