# Iteración 04-06 · Protección del historial ante borrados en cascada

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-06-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-06-redaccion.md)); D1 a D4 resueltas por el desarrollador el mismo día ([bitacora-04-06-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-06-cierre.md)).
- **Subfase del plan:** nueva (Auditoría 02); `definicion-epica-04.md`, alcance 6.
- **Depende de:** 04-01 (puede tocar `eliminar_cliente` al exigir POST; la 04-06 parte de lo que deje). Se redactó en paralelo a la vigilancia de la 03-05; ~~**su ejecución en local no empieza hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17). **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).**~~ **Superado el 2026-11-18 (RDA-021): no hay vigilancia que cerrar; la 14-01 se despliega antes de la 04-01 (RDA-022).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-10 → 04-02 → 04-03 → 04-04 → 04-05 → **04-06**.
- **RDA relacionadas:** RDA-007; RDA-017 (borrado físico con doble confirmación, **para usuarios**, Épica 09; ver «Contradicciones»).
- **Hallazgos que cierra:** AUD-02-001 (R14).
- **Clase de cambio esperada:** **Clase 1** (comportamiento de borrado gestionado por Django). **La iteración se detiene si `sqlmigrate` muestra cualquier `ALTER`** (decisión de la épica; `AGENTS.md`, regla 8.1).
- **Respaldo previo al despliegue:** **sí**, obligatorio: hay migración.
- **Archivos que tocará la ejecución:** `pedidos/models.py`, `pedidos/migrations/0008_…` (**consulta previa** para `makemigrations` y `migrate` en local, `AGENTS.md` sección 6), `pedidos/views.py` (`eliminar_cliente`), `pedidos/templates/pedidos/cliente_confirm_delete.html`, `pedidos/tests/test_regresiones.py` y pruebas nuevas.

## Objetivo

Que eliminar un cliente nunca borre sus pedidos, ítems, pagos, cotizaciones ni ítems de cotización, y que la pantalla le diga al usuario por qué no se puede, como ya hace la de productos.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main`, con archivo y línea.
- **Inferido:** sale de leer el código o la documentación de Django; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## Qué hay hoy (verificado)

### Relaciones (`pedidos/models.py`)

| Relación | Línea | `on_delete` | Tras la 04-06 |
| :------- | :---- | :---------- | :------------ |
| `Pedido.cliente` | `:37` | `CASCADE` | **`PROTECT`** |
| `Cotizacion.cliente` | `:164` | `CASCADE` | **`PROTECT`** |
| `Pago.pedido` | `:92` | `CASCADE` | sin cambio |
| `ItemPedido.pedido` | `:197` | `CASCADE` | sin cambio |
| `ItemCotizacion.cotizacion` | `:214` | `CASCADE` | sin cambio |
| `ItemPedido.producto`, `ItemCotizacion.producto` | `:198`, `:215` | `PROTECT` | sin cambio (modelo a seguir) |
| `Pedido.creado_por`, `Pago.registrado_por`, `RegistroEvento.usuario` | `:58`, `:97`, `:272` | `SET_NULL` | sin cambio (RDA-017) |

### Cadena de cascadas que sigue vigente

- **Pedido → ítems:** intencional. Los ítems no existen sin su pedido (composición); `editar_pedido` incluso los borra y recrea (`views.py:329`).
- **Cotización → ítems:** intencional, por la misma razón (`views.py:896`).
- **Pedido → pagos:** ~~**no consta que sea intencional.**~~ **Intencional (respondido el 2026-11-18, respuesta 1 del cliente, dicha por el desarrollador).** `eliminar_pedido` (`views.py:382`) borra el pedido y con él sus pagos, es decir, historial financiero. Ninguna RDA ni regla del cliente lo decide. **Fuera** de esta iteración (no es AUD-02-001); se registra como pregunta `PENDIENTE_CLIENTE` (registro, sección 2): ¿se puede eliminar un pedido con pagos?
- Con la 04-06, borrar un cliente **sin** historial no arrastra nada; **con** historial, se rechaza entero (Django revisa todos los objetos relacionados antes de borrar, inferido de la documentación de `PROTECT`).

### La vista y la pantalla

- `eliminar_cliente` (`views.py:690-697`): GET muestra la confirmación; POST llama a `cliente.delete()`, registra `cliente_eliminado` y redirige. **No captura `ProtectedError`**: con `PROTECT` y sin cambios, el POST daría error 500.
- `eliminar_producto` (`views.py:1122-1139`), el modelo a seguir: captura `ProtectedError` y vuelve a pintar la confirmación con `error`: «No se puede eliminar este producto porque ya forma parte de Pedidos o Cotizaciones históricas. Para mantener la integridad de los datos, no está permitido borrarlo.»
- `cliente_confirm_delete.html`: advierte «podrías perder el historial de sus pedidos asociados»; no tiene bloque para un error.

### Migraciones (numeración verificada)

`pedidos/migrations/` tiene `0001_initial` a `0007_registroevento`, sin huecos. La nueva será **`0008_…`**, con dependencia en `0007_registroevento` (nombre exacto lo da `makemigrations`; se propone `0008_proteger_historial_cliente` con `--name`).

### Flujos que borran clientes (búsqueda de `.delete()` en `pedidos/`)

| Flujo | ¿Borra clientes? | Efecto de `PROTECT` |
| :---- | :--------------- | :------------------ |
| `eliminar_cliente` (`views.py:693`) | Sí | Se rechaza si hay historial: se captura (alcance). |
| Admin de Django (`admin.py:6`, `ClienteAdmin`, acción de borrado por defecto) | Sí | El admin muestra su propia página «no se puede borrar por objetos protegidos» en vez de borrar en cascada (inferido de Django; se confirma en la réplica). Cambio deseado. |
| `purgar_registros` (única orden de gestión) | No (solo `RegistroEvento`, `eventos.py:74`) | Ninguno. |
| `eliminar_pedido`, `eliminar_cotizacion`, `eliminar_pago`, `editar_*` | No borran clientes | Ninguno. |
| Restauración (`restaurar_bd`) | Reemplaza tablas por SQL, no usa el ORM | Ninguno (las protecciones de Django no actúan en `mysql`). |
| Pruebas existentes | `test_eventos_negocio.py:119-122` y `test_bloqueo_envio.py:36` borran clientes **sin** historial; `test_acceso.py:139` intenta borrar uno con historial **como anónimo** (redirige, no borra); `test_cotizaciones.py:164` borra pedidos, no clientes | Siguen en verde (inferido; se confirma con la suite). |

No hay limpieza de datos ni comando que borre clientes con historial: nada se rompe salvo la cascada, que es lo que se quiere quitar.

## Contradicciones con la planificación

- **RDA-017 no aplica a clientes.** Su «borrado físico con doble confirmación» es para **usuarios** (Épica 09). Para clientes no hay RDA de borrado: esta iteración **no** agrega doble confirmación ni borrado lógico; solo impide borrar con historial. Si se quisiera archivar clientes, sería funcionalidad nueva.
- **R14 solo cubre pedidos.** `test_r14_eliminar_cliente_con_pedidos_se_rechaza` (`test_regresiones.py:376`) no prueba cotizaciones ni la vista; se agregan pruebas (tabla abajo) sin tocar el sentido de R14.
- **Pagos en cascada desde el pedido:** no es parte de AUD-02-001, pero es la misma clase de pérdida de historial. Registrado aparte, sin ampliar el alcance.

## Alcance

1. `Pedido.cliente` y `Cotizacion.cliente`: `CASCADE` → `PROTECT`.
2. Migración `0008` (Clase 1 esperada), con su `sqlmigrate` copiado en la bitácora.
3. `eliminar_cliente`: captura `ProtectedError` **fuera** de cualquier bloque atómico (regla 8.3), vuelve a pintar la confirmación con el mensaje de D1 y **no registra ningún evento** por el rechazo (D3).
4. `cliente_confirm_delete.html`: bloque de error como el de productos (según `DESIGN.md`) y advertencia «Solo se puede eliminar un cliente sin pedidos ni cotizaciones» (D2), **sin conteos y sin ocultar el botón**.
5. R14 pasa de fallo esperado a verde (se quita `@expectedFailure`) y se suman las tres pruebas de D4.
6. **Fuera:** pagos en cascada desde el pedido (~~pregunta `PENDIENTE_CLIENTE`, se conserva en el registro, sección 2~~ respondida el 2026-11-18: es intencional); borrado lógico o archivado de clientes; `require_POST` de `eliminar_cliente` (04-01); doble confirmación (RDA-017 es de usuarios).

## Decisiones (resueltas por el desarrollador, 2026-11-17)

| # | Decisión | Resuelta como |
| :- | :------- | :------------ |
| D1 | Mensaje de rechazo | «No se puede eliminar este cliente porque tiene pedidos o cotizaciones registrados. Para conservar su historial, no está permitido borrarlo.» |
| D2 | Advertencia de la confirmación (GET) | «Solo se puede eliminar un cliente sin pedidos ni cotizaciones», **sin contar pedidos y sin ocultar el botón**. |
| D3 | Evento por el rechazo | **No** se registra. `cliente_eliminado` solo cuando se borra. |
| D4 | Pruebas además de R14 | Cliente que solo tiene cotización; la vista **con** historial y **sin** historial. |

## Pasos

0. Respaldo de la réplica (`respaldo.md`) y consulta previa para `makemigrations` y `migrate` en local.
1. Línea base: `test pedidos` (número y fallos esperados tras la 04-05), `showmigrations pedidos` (hasta `0007`).
2. Pruebas primero (tabla siguiente); ver fallar las nuevas y R14 sin `@expectedFailure`.
3. Cambiar `on_delete` en `models.py:37` y `:164`.
4. `python manage.py makemigrations pedidos --name proteger_historial_cliente`: debe crear **solo** `0008` con dos `AlterField`.
5. **`python manage.py sqlmigrate pedidos 0008` en la réplica** y copiar la salida en la bitácora. **Esperado (inferido):** solo los comentarios `-- Alter field cliente on cotizacion` y `-- Alter field cliente on pedido`, **sin sentencias SQL**, porque `on_delete` lo aplica Django y la clave foránea en MySQL no cambia. **Si aparece cualquier `ALTER`, `DROP` o `ADD CONSTRAINT`: se detiene la iteración** y se replantea con el desarrollador.
6. `migrate` en local, vista, plantilla, pruebas en verde.
7. Revisión manual en la réplica: borrar un cliente con historial (mensaje, nada borrado, conteos iguales), uno sin historial (se borra) y el mismo intento desde el admin; escritorio y 360 px.
8. Bitácora (con el SQL de `sqlmigrate`), registro, auditoría (AUD-02-001), estado «En revisión».

## Cómo se comprueba que es Clase 1

| Comprobación | Esperado |
| :----------- | :------- |
| `sqlmigrate pedidos 0008` en la réplica | Sin sentencias SQL; cualquier `ALTER` detiene la iteración. |
| `SHOW CREATE TABLE pedidos_pedido` y `pedidos_cotizacion` antes y después de `migrate` en la réplica (la ejecuta el desarrollador: `mysql` requiere consulta) | Idénticos. |
| `makemigrations --check --dry-run` tras crear `0008` | «No changes detected». |
| Conteos de las seis tablas en la réplica antes y después de `migrate` | Iguales. |

## Pruebas

| Punto | Prueba |
| :---- | :----- |
| R14 | `test_r14_eliminar_cliente_con_pedidos_se_rechaza` sin `@expectedFailure`: `ProtectedError` y el pedido sigue. |
| Con `PROTECT`, solo cotización (D4) | `cliente.delete()` lanza `ProtectedError`; la cotización y sus ítems siguen. |
| Vista, con historial (D4) | POST a `/clientes/eliminar/<pk>/` con pedido y pago: 200, mensaje exacto de D1, **ningún evento nuevo** (D3), cliente, pedido, ítems y pago siguen. |
| Vista, sin historial (D4) | POST: redirige a la lista, cliente borrado, un evento `cliente_eliminado` (`test_eventos_negocio.py:119` ya lo cubre). |
| Confirmación (GET) | 200 con el texto de D2 y con el botón de eliminar presente. |
| Existentes | `test_acceso`, `test_bloqueo_envio`, `test_eventos_negocio` y `test_cotizaciones` en verde. |

Fallos esperados: uno menos que los que deje la 04-05 (R14 sale de la lista; tras la 04-01 quedarían R8, R9 y R15).

## Verificación en producción (la hace el desarrollador; **no verificado** hasta entonces)

1. Respaldo previo, descargado y verificado (`respaldo.md`).
2. `migrate` en la consola de PythonAnywhere: aplica `0008` sin error; `showmigrations pedidos` la marca.
3. Tras el Reload: abrir la confirmación de un cliente con historial (sin borrar) y ver el texto de D2. **No se intenta borrar un cliente real con historial** para probar: el camino se valida en la réplica.
4. `server.log` sin errores nuevos.
- **No verificado:** cuántos clientes de producción tienen historial ni si existen clientes sin pedidos ni cotizaciones (se puede contar en la réplica, solo conteos).

## Plan de retroceso

- `retroceso.md`, caso 2 (con migraciones; escrito para Clase 2, se aplica igual a esta de Clase 1): `python manage.py migrate pedidos 0007` (revierte `0008`; sin SQL, igual que al aplicarla, inferido) y luego volver a la etiqueta anterior y Reload. Si `migrate` atrás fallara, el respaldo previo y el caso 3.
- Orden: primero revertir la migración, después el código (el código viejo no conoce `0008`).

## Criterio de término

- `sqlmigrate` sin SQL, copiado en la bitácora.
- R14 y las pruebas nuevas en verde; el resto sin cambios.
- Revisión manual en la réplica hecha.
- AUD-02-001 resuelto en la auditoría; verificación de producción hecha.

## Riesgos

- **Protege el historial pero deja clientes sin borrar:** un cliente con un solo pedido antiguo ya no se puede eliminar, y no hay forma de archivarlo. Es el efecto buscado; si el negocio necesita «ocultar» clientes, es funcionalidad nueva (propuesta, no esta iteración).
- **`sqlmigrate` con `ALTER`:** si Django 6.0 llevara algo de `on_delete` a la base, la iteración se detiene (no se adapta sobre la marcha).
- **Pagos en cascada desde el pedido:** el historial financiero sigue expuesto por `eliminar_pedido`; queda la pregunta al cliente.
- **Botón visible aunque no se pueda borrar (D2):** el usuario puede intentarlo y recibir el rechazo; es lo decidido, coherente con productos.
- **Sin rastro del intento rechazado (D3):** si alguien insiste en borrar clientes con historial, no queda en los eventos; aceptado (no cambian datos).
- **Admin de Django:** cambia su comportamiento de borrado (mejor), sin pantalla propia; se revisa en la réplica.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-05.
