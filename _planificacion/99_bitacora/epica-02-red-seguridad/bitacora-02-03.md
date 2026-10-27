# Bitácora 02-03 · Pruebas de flujos críticos

- **Fecha:** 2026-10-26
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** En revisión

## Resumen

Se crearon `pedidos/tests/ayudas.py` (formato de `items_json`, método HTTP actual de cambiar estado y duplicar, hora congelada), `test_pedidos.py` (31 pruebas) y `test_cotizaciones.py` (9 pruebas): crear y editar pedidos y cotizaciones con ítems, convertir una cotización, cambiar estado, duplicar, la clasificación del panel y del trabajo semanal, el detalle del pedido e ingresar y editar pagos. Son de caracterización: fijan lo que pasa hoy. Las pruebas pasaron de 111 a 151, en `OK` en tres ejecuciones seguidas. No se tocó código de la aplicación. Quedan 3 hallazgos propuestos.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/tests/ayudas.py` | Nuevo: `items_json`, `cambiar_estado`, `duplicar`, `congelar_hora` y `MEDIODIA` |
| `pedidos/tests/test_pedidos.py` | Nuevo: 31 pruebas en 8 clases (ayudas, tareas 2, 3, 6, 7 y 8, detalle y pagos) |
| `pedidos/tests/test_cotizaciones.py` | Nuevo: 9 pruebas en 3 clases (tareas 4 y 5) |
| `docs/operacion/pruebas.md` | Tres filas en la sección 5 y sección 9 «Flujos fijados» |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-03-flujos-criticos.md` | Estado, decisiones D1 a D3 y criterios marcados |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, nombres de prueba en la sección 2, decisiones en la sección 3, 3 hallazgos propuestos en la sección 4 e historial |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-03.md` | Esta bitácora |

## Punto de partida verificado contra el código

| Punto | Resultado |
| :---- | :-------- |
| Rutas | Coinciden. El nombre de la vista es `cambiar_estado_pedido` (la ruta se llama `cambiar_estado`). Detalle del pedido: `/<pk>/` |
| `cambiar_estado` y `duplicar_pedido` escriben con GET | Coincide: ninguna comprueba el método |
| `items_json` y su `try/except` | Coincide en `crear_pedido`, `editar_pedido`, `crear_cotizacion` y `editar_cotizacion`: registran con `logger.exception`. Las cantidades pasan por `float()` (AUD-02-015) y el precio unitario es el que envía el navegador (hallazgo propuesto H1). Sin `items_json`, la edición conserva los ítems anteriores |
| `duplicar_pedido` | Copia cliente, resumen, detalles, valor, fecha de entrega e imagen (la misma ruta de archivo, no una copia), estado `PENDIENTE`. **No copia** ítems, pagos ni `creado_por` (queda nulo: hallazgo propuesto H3); `estado_pago` queda en `PENDIENTE` por el valor por defecto |
| `convertir_a_pedido` | Coincide: lee `fecha_entrega` y `valor_abonado` de `request.POST` sin formulario; `valor_abonado` no numérico o negativo se trata como 0; copia `valor_total` a `valor_venta`; el método por defecto del abono es `TRANSFERENCIA` (en `crear_pedido` es `EFECTIVO`). `fecha_entrega` vacía no se valida (hallazgo propuesto H2) |
| `cambiar_estado_pedido` (D3) | Acepta cualquier estado de `ESTADO_CHOICES` desde cualquier otro (avanzar, retroceder, saltar); un estado inexistente redirige al detalle sin cambios; solo registra evento si el estado cambia. **No hay reglas que contradigan el plan**: no fue necesario detenerse |
| `editar_cotizacion` | Diferencia no listada: una cotización `ACEPTADA` no se edita; GET y POST redirigen al detalle |
| Eventos (`eventos.py`) | Tipos usados: `pedido_creado`, `pedido_modificado`, `pedido_estado_cambiado`, `pedido_duplicado`, `pago_registrado`, `pago_modificado`, `cotizacion_convertida`. Crear y editar una cotización no dejan evento (inventario de 01-04) |
| Hora | `crear_cotizacion`, `convertir_a_pedido` y `trabajo_semanal` usan `timezone.now()` del módulo: basta parchar `django.utils.timezone.now`. Los `default=timezone.now` de los modelos no se alcanzan: la fecha de solicitud del duplicado se acota entre dos lecturas del reloj |
| Línea base | 111 pruebas en `OK`, como se esperaba |

## Hallazgos propuestos (sin corregir)

- **H1 · Precio del ítem enviado por el navegador.** El `precio_unitario` de cada ítem de pedido y de cotización se toma de `items_json` y se guarda sin compararlo con el catálogo; un ítem con precio $1 se acepta. Contradice `AGENTS.md`, sección 9 («nunca se confía en los datos que calcula el navegador»). Fijado en `CrearPedidoTests.test_el_precio_lo_envia_el_navegador`. Podría ampliar AUD-02-014. Severidad sugerida: Media.
- **H2 · Conversión con fecha de entrega vacía (por lectura, sin prueba).** `convertir_a_pedido` pasa `fecha_entrega` del POST directo a `Pedido.objects.create`; si llega vacía, el guardado del `DateField` falla y el decorador responde 500. La plantilla marca el campo `required`, así que solo ocurre fuera del navegador. Es un camino de fallo: no se probó aquí; candidato a la 02-04. Severidad sugerida: Baja.
- **H3 · Duplicado sin autor.** `duplicar_pedido` deja `creado_por` nulo: no copia el del original ni usa el usuario que duplica. Fijado en `DuplicarPedidoTests.test_lo_que_no_se_copia`. Severidad sugerida: Baja.
- Los tres quedaron en la sección 4 de `registro-pendientes.md`, sin número de auditoría.
- No se fijó `estado_pago` al crear un pedido con abono (hoy queda `PENDIENTE`): es la regresión R10 de la 02-04 (AUD-02-004) y una prueba de caracterización la contradiría.

## Verificación

### Línea base

```text
> python manage.py test pedidos
Found 111 test(s).
OK
```

### `python manage.py test pedidos -v 2`, tres ejecuciones seguidas

| Ejecución | Recuento | Resultado |
| :-------- | :------- | :-------- |
| 1 | `Ran 151 tests in 250.910s` | `OK` |
| 2 | `Ran 151 tests in 287.108s` | `OK` |
| 3 | `Ran 151 tests in 258.617s` | `OK` |

Las tres crean y destruyen `test_manzagrafica` y muestran la advertencia esperada `mysql.W002`. Pruebas nuevas de la ejecución 1, todas `ok`:

```text
test_cotizaciones.ConvertirCotizacionTests: test_abono, test_copia_cabecera_items_y_cierra_la_cotizacion,
  test_pantalla_sugiere_entrega_en_siete_dias, test_valor_venta_es_el_valor_total_sin_iva
test_cotizaciones.CrearCotizacionTests: test_fecha_de_vencimiento, test_formulario_responde_con_la_fecha_de_hoy,
  test_post_valido_crea_cotizacion_con_items
test_cotizaciones.EditarCotizacionTests: test_aceptada_no_se_edita, test_cambia_campos_y_reemplaza_items
test_pedidos.AyudasTests: test_cambiar_estado_usa_la_ruta_actual, test_congelar_hora_fija_timezone_now,
  test_duplicar_usa_la_ruta_actual, test_items_json_arma_el_formato_del_navegador
test_pedidos.CambiarEstadoTests: test_cualquier_transicion_se_acepta, test_estado_inexistente_redirige_sin_cambiar_nada,
  test_no_toca_el_estado_de_pago, test_pedido_inexistente_responde_404
test_pedidos.ClasificacionTests: test_panel, test_trabajo_semanal
test_pedidos.CrearPedidoTests: test_abono_inicial_crea_un_pago, test_el_precio_lo_envia_el_navegador,
  test_formulario_invalido_no_crea_nada, test_formulario_responde, test_post_valido_crea_pedido_con_items,
  test_precio_del_item_queda_congelado, test_sin_abono_no_hay_pagos, test_sin_items_json_crea_el_pedido_sin_items
test_pedidos.DetallePedidoTests: test_detalle_inexistente_responde_404, test_detalle_responde_con_el_pedido
test_pedidos.DuplicarPedidoTests: test_copia_cabecera_y_redirige_al_nuevo, test_fecha_de_solicitud_es_la_actual,
  test_lo_que_no_se_copia
test_pedidos.EditarPedidoTests: test_cambia_campos_y_valor_venta, test_formulario_responde_con_los_items_precargados,
  test_reemplaza_los_items, test_sin_items_json_conserva_los_items
test_pedidos.PagosTests: test_editar_pago_formulario_responde, test_editar_pago_recalcula_el_estado,
  test_ingresar_desde_el_pedido_sugiere_el_saldo, test_ingresar_pago
```

Recuento: 111 de la línea base + 31 de `test_pedidos.py` + 9 de `test_cotizaciones.py` = 151.

### Otros comandos

```text
> python manage.py test pedidos --exclude-tag regresion
Found 151 test(s).
Ran 151 tests in 241.315s
OK

> python manage.py check
System check identified no issues (0 silenced).

> python manage.py makemigrations --check --dry-run
No changes detected

> git status --short
 M _planificacion/00_producto/auditoria-tecnica.md
 M _planificacion/00_producto/registro-pendientes.md
 M _planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-03-flujos-criticos.md
 M _planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md
 M _planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02.md
 M docs/operacion/pruebas.md
?? _planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02-cierre.md
?? _planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-03.md
?? pedidos/tests/ayudas.py
?? pedidos/tests/test_cotizaciones.py
?? pedidos/tests/test_pedidos.py

> git diff --stat
 _planificacion/00_producto/auditoria-tecnica.md    |  2 +-
 _planificacion/00_producto/registro-pendientes.md  | 20 +++++++++++-----
 .../iteracion-02-03-flujos-criticos.md             | 26 +++++++++++----------
 .../iteracion-02-04-regresiones.md                 |  2 +-
 .../epica-02-red-seguridad/bitacora-02-02.md       | 12 ----------
 docs/operacion/pruebas.md                          | 27 +++++++++++++++++++++-
 6 files changed, 56 insertions(+), 33 deletions(-)
```

El diff incluye también el paso 1 (cierre de la 02-02: `auditoria-tecnica.md`, `iteracion-02-04`, `bitacora-02-02.md` y `bitacora-02-02-cierre.md`). Solo toca `pedidos/tests/` y archivos `.md`: ningún código de la aplicación.

- Revisión de pantallas en escritorio y a 360 px: no aplica, la iteración no toca plantillas ni estilos.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Existen `test_pedidos.py`, `test_cotizaciones.py` y `ayudas.py`, con pruebas de las tareas 2 a 8 (y de cada ayuda en `AyudasTests`).
- [x] El precio histórico se comprueba congelado (`test_precio_del_item_queda_congelado`: el ítem conserva $11.900 después de subir el producto).
- [x] Cada regla sin confirmar tiene `PENDIENTE_CLIENTE` y figura en la sección 2 del registro: ítems al duplicar, `ENTREGADO` atrasado, pedidos sin fecha y valor de la cotización.
- [x] Las pruebas que dependen del GET de cambiar estado y duplicar lo declaran en un comentario y pasan por `ayudas.cambiar_estado` y `ayudas.duplicar`.
- [x] Ninguna prueba escribe en el `media/` real (`DuplicarPedidoTests` usa `override_settings(MEDIA_ROOT=…)` con una carpeta temporal) ni ejecuta `mysql` o `mysqldump`.
- [x] `test pedidos` en verde en tres ejecuciones; `check` sin errores; `makemigrations --check --dry-run` sin cambios.
- [x] El diff no toca código de la aplicación.
- [x] D1, D2 y D3 resueltas por el desarrollador y registradas.

## Decisiones tomadas

- D1, D2 y D3 del desarrollador (2026-10-26), registradas en la iteración y en la sección 3 del registro.
- El formulario de pedido inválido registra una línea `INFO`; se absorbe con `assertLogs`. Ninguna otra prueba provoca errores a propósito.
- `test_dinero.py` conserva su propio `congelar_hora`; las pruebas nuevas usan el de `ayudas.py`. Unificarlos queda como limpieza menor.

## Pendientes y riesgos

- Para el desarrollador: decidir si H1, H2 y H3 pasan a la auditoría y a qué iteración (H2 podría sumarse a la 02-04).
- Cuando la 04-01 pase cambiar estado y duplicar a POST, se cambian `ayudas.cambiar_estado` y `ayudas.duplicar` y se revisan las pruebas marcadas en la sección 9 de `pruebas.md`.
- Cuando la 03-03 corrija `estado_pago` (AUD-02-004), puede cambiar el estado de pago que fijan `ConvertirCotizacionTests.test_abono` y `PagosTests`, que hoy coinciden con la regla correcta.

## Commit sugerido

`Épica 2 - Iteración 02-03: fija con 40 pruebas de caracterización los flujos de pedidos, cotizaciones, conversión, estados, duplicado y pagos, sin tocar el código de la aplicación`
