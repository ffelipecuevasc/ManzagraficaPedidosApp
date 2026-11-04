# Bitácora 03-02 · Erradicación de la supresión silenciosa (alcance B)

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión. Falta el conteo de pedidos sin ítems, que ejecuta el desarrollador.

## Resumen

Se aplicó el alcance B (decisión del desarrollador): en `crear_pedido` desaparece el `try/except Exception` de los ítems y la excepción sale del `transaction.atomic` que la vista ya tenía. Si un ítem falla, se revierten el pedido, los ítems y el pago, y Django responde 500 con la página de la 01-03 y una sola línea `django.request` con traza. R3 pasó a verde y se retiró como regresión: los fallos esperados bajan de 18 a 17. No se tocaron las capturas de `editar_pedido` ni de cotizaciones (03-03), las de respaldo y restauración (04-04), el abono de `views.py:858` (03-03), los `float` (07-02), R1, R2 ni R4. Sin despliegue propio: viaja con la 03-05.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/views.py:178-192` | `crear_pedido`: sin `try/except Exception` en los ítems; comentario de tres líneas que explica que la excepción sale del `atomic`. Sin otro cambio (18 líneas menos de captura, 3 de comentario). |
| `pedidos/tests/test_pedidos.py:166-228` | Clase nueva `CrearPedidoItemFallidoTests` (3 pruebas, la primera con 5 casos), escrita antes de corregir. Imports nuevos: `inspect`, `json`, `views` y `formatear_como_error_log`. |
| `pedidos/tests/test_regresiones.py:8-9` y `:156-165` | R3 sin `@expectedFailure` ni `@tag('regresion')`, con `raise_request_exception = False` y `absorber_errores` de `pedidos` y `django.request`. Nota en la numeración del encabezado. R1, R2 y R4 sin cambios. |
| `pedidos/tests/test_capturas_amplias.py:43` | Solo el texto del docstring de `CapturasItemsTests`: «el fondo de estas tres queda en la 03-03». Sin cambio de lógica. |
| `docs/operacion/pruebas.md:99`, `:122` | Valor vigente 17; fila de R3 retirada de la tabla; viñeta que explica la retirada. |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/iteracion-03-02-erradicacion-supresion-silenciosa.md` | Estado «En revisión», decisiones resueltas, tareas y criterios (el conteo P3 y la revisión manual, sin marcar). |
| `_planificacion/00_producto/registro-pendientes.md` | Líneas `:6`, `:7`, `:16`, fila 03-02 (`:44`), nota en el pendiente del conteo (`:196`) e historial (`:305`). |
| `_planificacion/00_producto/auditoria-tecnica.md` | Notas fechadas en AUD-02-008 (`:73`) y AUD-01-002 (`:24`). Estados sin cambio. |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-02.md` | Esta bitácora (nueva). |

## Diff de `crear_pedido`

```diff
                 # 2. Procesar los Ítems (Hijos)
+                # Si un ítem falla, la excepción sale del bloque atomic: se revierte todo (pedido, ítems
+                # y pago) y Django responde 500 con la traza en server.log (03-02, RDA-019).
+                # El aviso al usuario y la conservación del formulario son de la 03-04.
                 items_json = request.POST.get('items_json')
                 if items_json:
-                    try:
-                        data_items = json.loads(items_json)
-                        for item in data_items:
-                            ...
-                    except Exception as e:
-                        # Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en server.log.
-                        logger.exception('Error procesando items del pedido %s', pedido.pk,
-                                         extra={'request': request})
-                        # No detenemos el proceso, los items son recuperables o editables
+                    data_items = json.loads(items_json)
+                    for item in data_items:
+                        ...
```

El cuerpo del bucle (`Producto.objects.get`, `ItemPedido.objects.create` con `float(...)` e `int(...)`) queda igual, con una sangría menos. Con el pago inicial y el evento ocurre lo mismo: si un ítem falla no se llega a ellos, y si todo sale bien el flujo no cambia.

## Verificación

Todo con `DB_NAME=manzagrafica_replica` en la sesión y el MySQL local de Docker encendido. Las pruebas usan la base `test_manzagrafica`.

### Antes de corregir (solo con las pruebas escritas)

`python manage.py test` sobre `CrearPedidoItemFallidoTests` y `ItemsTodoONadaTests`: 7 pruebas, `FAILED (failures=8, expected failures=3)`.

- **4 pruebas fallaban** (8 fallos contando los 5 casos de la primera), todas por el motivo esperado:
  - `test_item_fallido_no_deja_rastro_y_responde_500` (5 casos): no hay registro `ERROR` en `django.request`, porque la vista respondía 302.
  - `test_item_fallido_deja_una_sola_linea_con_traza`: el registrador era `pedidos.views`, no `django.request`.
  - `test_crear_pedido_no_tiene_captura_amplia`: `except Exception` presente.
  - `test_r3_crear_pedido_con_item_fallido_no_deja_rastro` (R3 ya sin marcas): `(1, 1) != (0, 0)`. Falla por la aserción de los datos, no por un error.
- R1, R2 y R4 (sin tocar): 3 fallos esperados.

### Después de corregir

- Pruebas del dominio tocado (`test_pedidos`, `test_regresiones`, `test_capturas_amplias`): 61 pruebas, `OK (expected failures=17)`.
- Suite completa, `python manage.py test pedidos`: **189 pruebas** (186 más las 3 nuevas), `OK (expected failures=17)` en tres ejecuciones (296 s, 265 s y 304 s). Sin `unexpected successes` ni `failures`.
- `python manage.py check` → sin problemas.
- `python manage.py makemigrations --check --dry-run` → `No changes detected`.

## Migraciones

- Ninguna.

## Lo que verifican las pruebas nuevas

- **Cinco causas de fallo** de un ítem: producto inexistente, JSON inválido, clave ausente, cantidad no numérica y precio no numérico. En todas: respuesta 500 con `pedidos/errors/500.html`, y 0 pedidos, 0 ítems, 0 pagos y 0 eventos (el pedido de la prueba lleva abono inicial, así que también se comprueba que el pago se revierte).
- **Una sola línea** de error, del registrador `django.request`, con método, ruta, usuario, `excepcion=DoesNotExist` y traza; sin el contenido del formulario.
- `crear_pedido` ya no contiene `except Exception` (se lee su fuente con `inspect`).

## Decisiones tomadas

Decisiones del desarrollador del 2026-11-04:

1. Alcance B: propagar el error solo en `crear_pedido`.
2. La 03-02 viaja con la 03-05.
3. Respaldo y restauración, hasta la 04-04; el abono de `:858`, en la 03-03; `float`/`Decimal`, en la 07-02.
4. El conteo de pedidos sin ítems lo ejecuta el desarrollador durante la 03-02 y lo repite tras el refresco de la réplica.

Decisiones del agente dentro del alcance:

- R3 se ajustó con `raise_request_exception = False` dentro de su propia prueba (no en `setUp`), para no tocar R1, R2 y R4.
- No se escribió una RDA: el alcance B no contradice RDA-019, que ya fija la captura fuera del bloque y la atomicidad explícita. Si prefieres dejar constancia formal, se agrega.
- Se actualizó el docstring de `CapturasItemsTests` (solo texto), porque decía que el fondo de las tres capturas quedaba en la 03-02.

## Conteo de pedidos sin ítems (para el desarrollador, criterio sin marcar)

Las tres consultas están en la iteración, sección «Evidencia P3», listas para copiar: solo `SELECT` y solo agregados (totales, sin ítems, sin ítems posteriores al primero con ítems, con valor, y por mes en UTC). Se ejecutan contra la réplica y se transcriben aquí los números, con la fecha del último refresco. El agente no las ejecutó.

| Consulta | Resultado (fecha del último refresco de la réplica: volcado del 2026-10-25 21:02:34, más la conversión de prueba del 2026-11-04) |
| :------- | :------ |
| 1 · pedidos | `PENDIENTE_DESARROLLADOR` |
| 2 · cotizaciones | `PENDIENTE_DESARROLLADOR` |
| 3 · por mes | `PENDIENTE_DESARROLLADOR` |

Se repite tras el refresco de la réplica (AUD-05-002, al cerrar la Épica 03). Limitaciones: no es el estado actual de producción; «sin ítems» es un indicio, no prueba de fallo; no detecta ítems parciales.

## Pendientes y riesgos

- **Revisión manual** (la hace el desarrollador, `AGENTS.md` sección 10, paso 5): contra la réplica, en escritorio y a 360 px, comprobar que al crear un pedido con un ítem fallido se ve la página 500 de la aplicación. No se hizo desde aquí. Una forma de provocarlo: enviar el formulario con un producto que se borró de la pantalla en otra pestaña. Criterio sin marcar en la iteración.
- **Hasta la 03-04**, un ítem fallido al crear un pedido muestra la página 500 y el formulario se pierde. Los datos quedan íntegros (se revierte todo). El mensaje y la conservación del formulario son de la 03-04.
- **Imagen de referencia:** si el pedido se revierte, el archivo subido queda en disco. La épica deja esa decisión para la 03-03.
- **Comentarios de `views.py`:** las tres capturas de `editar_pedido`, `crear_cotizacion` y `editar_cotizacion` siguen diciendo «se corrige en 03-02». Quedan para actualizar en la 03-03, porque no se tocan aquí.
- **R1, R2 y R4:** cuando la 03-03 haga que la excepción salga de esas vistas, deberán ajustarse como R3 (`raise_request_exception = False`), o fallarán por el error y no por los datos. Anotado en `pruebas.md`.
- **Producción:** cuando se despliegue con la 03-05, los errores de ítems de `crear_pedido` aparecerán con `registrador=django.request` y no con `pedidos.views`.
- **AUD-02-008:** R3 pasó a verde aquí, pero su fila decía que cierra en la 03-03. Se agregó una nota fechada y el estado sigue «Abierto»: lo decides tú. AUD-01-002 sigue con avance y cierra en la 03-03.

## Criterios de aceptación

Ver la iteración: marcados todos los de código y pruebas; sin marcar el conteo P3 y la revisión manual.

## Commit sugerido

`Épica 3 - Iteración 03-02: crear_pedido propaga el error de un ítem y revierte todo, R3 pasa a verde y los fallos esperados bajan de 18 a 17`
