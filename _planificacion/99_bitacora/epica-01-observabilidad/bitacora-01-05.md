# Bitácora 01-05 · Consulta de eventos en el admin

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (2026-10-25, revisada por el desarrollador, con la revisión manual de [evidencia-01-05](../../10_epicas/epica-01-observabilidad/evidencia-01-05.md)); sin desplegar; se despliega en 01-06. **Sin migraciones.**

## Resumen

- **`RegistroEventoAdmin`** en `pedidos/admin.py` (diff aprobado):
  - **Listado:** fecha en hora de Chile con su zona, tipo, usuario, entidad, identificador y resumen.
  - **Filtros:** fecha (`DateFieldListFilter`), tipo y usuario (solo los que tienen eventos).
  - **Búsqueda:** exacta por identificador de la entidad.
  - **Rendimiento:** `list_select_related('usuario')`.
  - **Acceso:** solo lectura y solo superusuarios.
- **Sin `date_hierarchy`** (decisión del desarrollador): contradice la regla técnica 6.
- **Zona horaria:** no requirió tocar `settings.py`.
- **9 pruebas nuevas** en `pedidos/tests/test_admin_eventos.py`. En total son 72, en verde tres veces.
- **Ajuste y cierre de la 01-04:** el acceso fallido guarda el nombre solo si existe como usuario. El detalle está en bitacora-01-04, sección «Ajuste del acceso fallido».

## Zona horaria (consulta obligatoria)

- **Estado actual:** `TIME_ZONE = 'America/Santiago'`, `USE_TZ = True` y `LANGUAGE_CODE = 'es-cl'`. La base guarda UTC y Django convierte a la zona activa al mostrar, así que el admin ya muestra hora de Chile. **No hace falta cambiar `settings.py`**, y no hay nada pendiente para 06-01 por este punto.
- **Zona visible junto a la fecha**, como pide la iteración: la columna «Momento (hora de Chile)» muestra, por ejemplo, `15-07-2026 14:05:09 (UTC-0400)`. El desfase cambia solo entre el horario de verano (`UTC-0300`) y el de invierno (`UTC-0400`). Una prueba lo comprueba con una fecha de invierno, en el listado y en el detalle.
- **Filtro por fecha:** `DateFieldListFilter` arma «Hoy», «Últimos 7 días», «Este mes» y «Este año» con `__gte` y `__lt` sobre instantes calculados en hora local. No usa funciones de truncado ni de extracción, de acuerdo con la regla 6. Una prueba comprueba que un evento de las 23:30 de Chile del día anterior, que en UTC ya es «hoy», no aparece en el día de hoy.

## Decisiones del desarrollador (2026-10-25)

1. **Diff de `pedidos/admin.py`** aprobado tal cual.
2. **Sin `date_hierarchy`.** Para armar la jerarquía, Django trunca las fechas con conversión de zona horaria en MySQL (`CONVERT_TZ`): no usa índices y devuelve nulo si faltan las tablas de zona horaria. Eso es lo que prohíbe la regla técnica 6 de `AGENTS.md`. La tarea queda cubierta con el filtro por fecha. Registrada en «Decisiones de la épica» y en la tarea 1 de la iteración.

## Diseño

- **Solo lectura:** `has_add_permission`, `has_change_permission` y `has_delete_permission` devuelven `False`. El detalle se muestra con todos los campos de solo lectura, sin «Guardar» ni «Eliminar». El listado queda sin acciones (desaparece «Eliminar seleccionados»). La limpieza es tarea de `purgar_registros`.
- **Solo superusuarios:** `has_module_permission` y `has_view_permission` exigen `is_active` y `is_superuser`. Un usuario del equipo sin superusuario no ve el modelo en el índice y recibe 403 en el listado y en el detalle, **aunque tenga los permisos del modelo asignados**.
- **Búsqueda `=entidad_id`:** es exacta. «12» no devuelve el 120. Un término no numérico no falla: devuelve 0 filas.
- **Sin consultas por fila:** el usuario se carga en la misma consulta del listado. El filtro de usuario (`RelatedOnlyFieldListFilter`) agrega una consulta fija, que no depende del número de filas.
- **Ruta del admin:** el admin vive en `acceso-manzagrafica-admin/`, no en `/admin/`. Las pruebas usan `reverse('admin:…')` para no repetir la ruta.

## Verificación

PowerShell 7, `DB_NAME=manzagrafica_replica`.

| Criterio | Prueba (`test_admin_eventos.py`) |
| :------- | :------------------------------- |
| El superusuario ve el listado; la búsqueda por identificador devuelve exactamente las filas de esa entidad | `test_listado_y_busqueda_por_identificador_de_entidad`, `test_busqueda_no_numerica_no_falla` |
| Filtros por tipo y por usuario | `test_filtros_por_tipo_y_por_usuario` |
| Filtro por fecha con el día de Chile | `test_filtro_por_fecha_usa_el_dia_de_chile` |
| Hora de Chile con su zona, en el listado y en el detalle | `test_fecha_en_hora_de_chile_con_su_zona` |
| `is_staff` sin superusuario: modelo oculto y 403 | `test_staff_sin_superusuario_no_ve_el_modelo_aunque_tenga_permisos`; además, un usuario sin `is_staff` es enviado al acceso del admin (`test_usuario_sin_staff_es_enviado_al_acceso`) |
| Sin agregar, modificar ni eliminar | `test_sin_agregar_modificar_ni_eliminar` (403 en agregar y eliminar, detalle sin guardar, un POST no cambia nada, listado sin acciones) |
| Consultas iguales con 1 y con 20 filas | `test_consultas_no_crecen_con_las_filas` (cuenta las consultas con 1 fila y exige el mismo número con 20, con 3 usuarios distintos) |

- `python manage.py test pedidos`: **72 pruebas en `OK`** en tres ejecuciones (58,3 s, 67,8 s y 59,2 s).
- `python manage.py check`: sin problemas.
- `makemigrations --check --dry-run`: `No changes detected`. **Sin migraciones**: `RegistroEventoAdmin` no cambia el modelo.
- **Revisión manual en la réplica:** hecha por el desarrollador el 2026-10-25 con los pasos de [evidencia-01-05](../../10_epicas/epica-01-observabilidad/evidencia-01-05.md). El agente no inició sesión ni arrancó el servidor. Ver «Revisión manual del desarrollador».

## Desviaciones y observaciones

- **«Jerarquía por fecha»** se reemplazó por el filtro por fecha (decisión del desarrollador, arriba).
- **La revisión manual crea filas en la réplica:** iniciar sesión deja eventos `acceso_exitoso` y `acceso_fallido`. Es esperado y sirve de evidencia. La réplica se refresca con el próximo volcado.
- **El número exacto de consultas del listado** no se fijó en la prueba (depende de la sesión y de los filtros). La prueba compara 1 fila contra 20, que es lo que pide el criterio.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/admin.py` | `RegistroEventoAdmin` (aprobado) |
| `pedidos/senales.py` | Ajuste de 01-04: acceso fallido sin lo escrito |
| `pedidos/tests/test_admin_eventos.py` | Nuevo: 9 pruebas |
| `pedidos/tests/test_eventos_negocio.py` | Ajuste de 01-04: 3 pruebas del acceso fallido |
| `docs/operacion/pruebas.md` | Tabla de archivos de prueba |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-05.md` | Nuevo: revisión manual |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-04-eventos-negocio.md`, `iteracion-01-05-admin-registros.md` | Cierre de 01-04 con su ajuste; estado y criterios de 01-05 |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Estados y decisiones (acceso fallido; sin `date_hierarchy`) |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | Nota para 04-04: restauración y tabla de eventos |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-04.md` | Estado final y sección del ajuste |
| `_planificacion/00_producto/registro-pendientes.md` | Cierre de 01-04, estado de 01-05, evidencia pendiente e historial |

## Despliegue

- **Sin migraciones.** Viaja en 01-06, que exige respaldo previo por la 0007 de la 01-01.
- En 01-06, la acción de prueba de la evidencia debe aparecer en este admin con su usuario.

## Pendientes

- Revisión del desarrollador.

## Revisión manual del desarrollador (2026-10-25)

Resultados integrados en [evidencia-01-05](../../10_epicas/epica-01-observabilidad/evidencia-01-05.md), sección «Respuesta del desarrollador».

- **9 puntos verificados en la réplica:** listado, hora de Chile con `(UTC-0300)`, acceso fallido con nombre inexistente («usuario desconocido») y con un usuario existente (solo su nombre), accesos exitosos, solo lectura en el listado y en el detalle, búsqueda exacta (`1` no trae el `10`), filtro por tipo (3 accesos fallidos de 8) y detalle.
- **Eventos generados:** de 0 a 8 filas (5 accesos exitosos y 3 fallidos). Confirma en un entorno real las señales de la 01-04 y su ajuste.
- **Observación de la vista a 360 px:** la tabla es más ancha que la pantalla y se desplaza en horizontal para ver usuario, entidad, identificador y resumen. Es el comportamiento normal de las tablas del admin de Django en pantallas angostas, **no un defecto**. No requiere cambios.
- **Salida de consola:** la petición a `/favicon.ico` (404) salió en la terminal desde `django.server`, que existe solo en `runserver`. No contradice la decisión de que los 404 no vayan a `error.log`: en PythonAnywhere no hay `django.server` y `django.request` sigue en `ERROR`.
