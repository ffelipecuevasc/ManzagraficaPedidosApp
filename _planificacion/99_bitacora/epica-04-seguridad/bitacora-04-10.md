# Bitácora 04-10 · Ejecución en local

- **Fecha:** 2026-11-18
- **Iteración:** [04-10 · Confirmación reforzada al eliminar un pedido con pagos](../../10_epicas/epica-04-seguridad/iteracion-04-10-confirmacion-reforzada-al-eliminar-un-pedido-con-pagos.md)
- **Estado resultante:** **Implementada, pendiente de revisión manual y despliegue.**
- **Base:** `main` en `ab7ce82` (tras el cierre de la 04-01), más el ajuste documental de la numeración de la 14-02 (commit aparte, sin código).
- **Hallazgos:** ninguno se cierra (la iteración no cierra hallazgos). Sin hallazgos nuevos; una contradicción de formato de montos (sección «Contradicciones»).

## Archivos modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/views.py` | `eliminar_pedido`: el pedido se lee con `annotate(cantidad_pagos=Count('pagos'), total_pagos=Coalesce(Sum('pagos__monto'), Value(0)))`. En el POST, la lectura, la comprobación (cantidad vista contra real, D4; `ELIMINAR` exacto con `strip()` si hay pagos, D2 y D3), `delete()` y el evento van en **un** `transaction.atomic()`. Si falta la confirmación o cambió la cantidad, no se borra y se repinta con el mensaje (200). Evento `pedido_eliminado` con `Pedido #N eliminado, con K pago(s)` o `sin pagos` (D1). Sin importaciones nuevas (`Count`, `Sum`, `Value` y `Coalesce` ya estaban). |
| `pedidos/templates/pedidos/pedido_confirm_delete.html` | `{% load humanize %}`; mensaje de error con `role="alert"`; aviso `id="aviso-pagos"` con cantidad (singular y plural con `pluralize`) y monto (`intcomma`); línea «Este pedido no tiene pagos registrados.» sin pagos; campo oculto `pagos_vistos` (con `stringformat:'d'`, para que una cantidad de 1.000 o más no salga con separador, como AUD-05-010); campo `confirmacion` con `label`, `aria-describedby="aviso-pagos"` y anillo de foco, solo con pagos. Se conserva `data-bloquear-envio`. CRLF conservado. |
| `pedidos/tests/test_eliminar_pedido.py` | Nuevo: 16 pruebas (aviso, singular y plural, `ELIMINAR` exacto, sin confirmación, cantidad cambiada, sin pagos, evento, un solo `atomic`, fallo de `delete()`, consultas). |

Sin `models.py`, sin migraciones, sin configuración, sin estáticos (Tailwind se carga por CDN en `base.html`, así que las clases nuevas no requieren compilar ni `collectstatic`).

## Pruebas

- **Línea base (antes de tocar código):** `python manage.py test pedidos` → `Ran 282 tests`, `OK (expected failures=4)`.
- **Pruebas nuevas contra el código anterior:** las 16 fallaron (17 fallos con los subcasos) por los motivos esperados: sin aviso, sin campo, borrado sin confirmación (302 en vez de 200), resumen sin la cantidad y recuento fuera de un `atomic` propio de la vista. Dos fallaron además por un error de la prueba (la lista es `/pedidos/lista/`), corregido.
- **Después:** `Ran 298 tests`, `OK (expected failures=4)` (282 + 16). Las existentes `test_eventos_negocio.test_pedido_eliminado` (tipo y entidad), `test_bloqueo_envio` y `test_acceso` siguen en verde sin cambios.
- `python manage.py check`: sin problemas. `python manage.py makemigrations --check --dry-run`: `No changes detected`. `showmigrations pedidos` no cambió (en la base de desarrollo local la `0007` figura sin aplicar; no se tocó).

## Consultas (excepción de `AGENTS.md`, sección 11)

Medidas con `CaptureQueriesContext` sobre un pedido con 2 pagos, sin contar los `SAVEPOINT` que agrega `TestCase`:

| Pantalla | Antes | Después |
| :------- | ----: | ------: |
| GET de confirmación | 4 | 4 |
| POST con pagos y `ELIMINAR` | 6 | 6 |

**+0 en ambas:** el agregado va como anotación en la misma consulta que lee el pedido, así que la excepción de +1 no se usó. Las pruebas `ConsultasTests` fijan el techo en antes + 1.

## Contradicciones

- **Formato del monto (`PENDIENTE_DESARROLLADOR`).** La iteración dice que `intcomma` «respeta el separador de miles con punto de `es-cl`» y pide `$15.000` (también `AGENTS.md`, regla 7.1). **No es así en Django 6:** con `es-cl`, `intcomma` pone un espacio duro (`$45 000`), lo mismo que ya probó la 14-01 para los ids. Toda la aplicación muestra los montos así. No se creó un formato propio solo para esta pantalla: se usa `intcomma`, como el resto, y las pruebas fijan el formato real. Decidir si se corrige el formato de montos en toda la aplicación (por ejemplo con `FORMAT_MODULE_PATH` o un filtro propio) y en qué iteración; afecta también a AUD-05-013.
- **Paso 2 (evidencia previa con SQL en la réplica):** es del desarrollador y **no se ejecutó** (`mysql` exige consulta previa). Pendiente suyo: los tres conteos de la iteración.
- **Paso 0 (respaldo de la réplica) y paso 5 (revisión manual):** no los hizo el agente.

## Decisiones de implementación

- **Cuándo se compara la cantidad vista:** si el formulario trae `pagos_vistos`, se compara siempre (también si se vio sin pagos y aparecieron, o se vio con pagos y ya no hay). Si no lo trae y el pedido no tiene pagos, se borra como antes (compatibilidad con un formulario abierto antes del despliegue). Si no lo trae y hay pagos, no se borra.
- **Orden de los mensajes:** si cambió la cantidad, gana el mensaje de cambio, aunque la palabra también falte.
- **Sin bloqueo de filas:** el recuento y el borrado van en la misma transacción, pero sin `select_for_update` (no se combina con `GROUP BY`). Con un solo worker y peticiones en serie, el riesgo es despreciable (inferido).

## Criterio de término

- [x] Tabla de pruebas en verde; resto de la suite sin cambios (`OK (expected failures=4)`).
- [ ] Revisión manual en la réplica (con y sin pagos, escritorio, 360 px y teclado): **pendiente del desarrollador**.
- [x] Sin migración nueva; consultas antes y después anotadas.
- [ ] Verificación 2 de producción: pendiente del despliegue.

## No verificado

- La pantalla en un navegador real: contraste, foco visible, lectura de `role="alert"` con lector de pantalla y diseño a 360 px.
- Los conteos del paso 2 en la réplica.
- Producción completa.

## Despliegue (lo hace el desarrollador)

1. Revisión manual en la réplica: un pedido **con** pagos (aviso con cifras; enviar sin palabra; con `eliminar`; con `ELIMINAR` y borrado correcto), uno **sin** pagos (como antes) y el evento en el admin. A 360 px y solo con teclado (Tab hasta el campo, foco visible, Enter).
2. Respaldo de rutina (`respaldo.md`): no hay migración.
3. Commit y etiqueta anotada. **Etiqueta:** la iteración no la fija; la propuesta de [bitacora-04-revision-final](bitacora-04-revision-final.md), sección 2, es `v4.2-confirmar-eliminar-pedido` (`PENDIENTE_DESARROLLADOR`).
4. Antes de subir: `git diff --stat v4.1-mutaciones-post -- requirements.txt pedidos/migrations PedidosApp/settings.py` **sin salida**. No cambian estáticos: **sin `collectstatic`**.
5. En PythonAnywhere: `git fetch --tags`, `git checkout <etiqueta>` y Reload.
6. Día 0: abrir la pantalla de eliminar de un pedido **con** pagos y ver el aviso **sin enviar**; con un **pedido de prueba** creado para eso, eliminarlo con y sin pagos y ver los eventos `… con K pagos` y `… sin pagos`. No se elimina un pedido real. `server.log` y `error.log` sin errores nuevos.
7. Retroceso: `retroceso.md`, caso 1, a `v4.1-mutaciones-post` y Reload. Los eventos con el resumen nuevo quedan y son inofensivos.

## Siguiente

Redactar la 14-02 (copiar los ítems al duplicar, AUD-05-012).
