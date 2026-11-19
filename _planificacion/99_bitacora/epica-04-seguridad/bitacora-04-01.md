# Bitácora 04-01 · Ejecución en local

- **Fecha:** 2026-11-18
- **Iteración:** [04-01 · Mutaciones solo por POST](../../10_epicas/epica-04-seguridad/iteracion-04-01-mutaciones-solo-por-post.md)
- **Estado resultante:** Implementada, pendiente de revisión manual y despliegue. No está Terminada.
- **Base:** `main` en `46fe24b` (tras la 14-01). El código de las cuatro vistas coincidía con lo descrito en la iteración: no hubo contradicciones que detuvieran el trabajo.
- **Hallazgos:** AUD-02-002, AUD-02-006 (parte GET), AUD-02-028 y AUD-03-002, corregidos en código y pendientes de verificar en producción. AUD-03-002 se cierra solo con un respaldo real desde la web.

## Archivos modificados

| Archivo | Cambio | Fin de línea |
| :------ | :----- | :----------- |
| `pedidos/views.py` | `@require_POST` como decorador más interno en `cambiar_estado_pedido`, `duplicar_pedido` y `generar_respaldo_bd`; `creado_por=request.user` al duplicar | LF, conservado |
| `pedidos/templates/pedidos/pedido_detail.html` | Iniciar y terminar pedido: formularios POST con `{% csrf_token %}` y `data-bloquear-envio`. Reabrir: botón `submit` con `data-confirm` dentro de un formulario POST (sin `data-url`). «Confirmar» del modal: `<button type="button">` | CRLF, conservado |
| `pedidos/templates/pedidos/respaldar_bd.html` | Formulario POST sin `onclick`/`location.reload`, con `data-bloquear-envio="Generando…"` y `data-desbloquear-ms="10000"` | CRLF, conservado |
| `pedidos/templates/pedidos/pago_confirm_delete.html` | **Nueva** (P1), con el patrón de `pedido_confirm_delete.html` | CRLF, como sus hermanas |
| `pedidos/static/pedidos/js/index.js` | `initDetailModals()`: «Confirmar» envía el formulario del disparador con `requestSubmit()`; `initBloqueoEnvio()`: atributo opcional `data-desbloquear-ms` | CRLF, conservado |
| `pedidos/tests/ayudas.py` | `cambiar_estado` y `duplicar` con POST | LF |
| `pedidos/tests/test_mutaciones_post.py` | **Nuevo**, 9 pruebas | LF |
| `pedidos/tests/test_regresiones.py` | Sin `@expectedFailure` en R6a, R6b, R6c, R7 y R19; encabezado actualizado | CRLF, conservado |
| `pedidos/tests/test_acceso.py` | `PkInexistenteTests`: `SOLO_POST_404` (cambiar, duplicar) y `eliminar_pago` en la lista con GET; una prueba nueva | LF |
| `pedidos/tests/test_errores.py` | Retirada `test_regresion_eliminar_pago_deja_tipo_y_traza` | CRLF, conservado |
| `pedidos/tests/test_eventos_negocio.py`, `test_capturas_amplias.py`, `test_contrato_error.py`, `test_pedidos.py` | GET → POST en las rutas que pasan a solo POST; `test_lo_que_no_se_copia` espera el autor | conservados |

No toca el panel (P2, 06-01), `eliminar_pedido` (04-10), qué se copia al duplicar ni la fecha mínima de entrega. Sin migraciones, dependencias ni configuración. **Sí cambia un estático (`index.js`)**: el despliegue necesita `collectstatic`.

## Pruebas

| Momento | Comando | Resultado |
| :------ | :------ | :-------- |
| Línea base | `python manage.py test pedidos` | `Found 273 test(s)` · `OK (expected failures=9)` |
| Pruebas nuevas antes del arreglo (con las ayudas ya en POST) | `python manage.py test pedidos.tests.test_mutaciones_post` | `Ran 9 tests` · `FAILED (failures=6, errors=1)`. Fallan: duplicar sin autor, las tres de plantillas (enlaces en vez de formularios, `location.reload`) y la confirmación de eliminar pago (`TemplateDoesNotExist`, error). Pasan ya antes: POST a cambiar estado (POST siempre funcionó; el GET → 405 lo afirma R6a), el anónimo a acceso (302) y el 404 de pago inexistente |
| Primera suite completa con el arreglo | `python manage.py test pedidos` | `Ran 282 tests` · `FAILED (failures=1, expected failures=4)`: `test_pedidos.DuplicarPedidoTests.test_lo_que_no_se_copia` afirmaba `creado_por` nulo. Se actualizó a la regla nueva |
| Suite completa final | `python manage.py test pedidos` | `Found 282 test(s)` · `OK (expected failures=4)` (quedan R8, R9, R14 y R15) |
| Configuración | `python manage.py check` | `System check identified no issues (0 silenced).` |
| Migraciones | `python manage.py makemigrations --check --dry-run` | `No changes detected` |

Cuenta: 273 + 9 (`test_mutaciones_post.py`) + 1 (`test_acceso`, 404 con POST) − 1 (retirada de `test_errores`) = 282.

**Orden de decoradores comprobado:** `PostAnonimoTests` y `BaseDeDatosPermisosTests` (302 al acceso) siguen en verde sin cambios, y la prueba nueva del anónimo con GET da 302, no 405.

**Prueba retirada:** `test_errores.test_regresion_eliminar_pago_deja_tipo_y_traza` afirmaba el 500 de AUD-02-002 «mientras exista». Con `pago_confirm_delete.html` el GET responde 200 y no hay error que registrar. La traza completa en el registro la siguen cubriendo las otras pruebas de `test_errores.py` (fallo forzado en la vista).

## Decisión: bloqueo del botón del respaldo

- **Lo que se vio en el código:** `generar_respaldo_bd` responde con `FileResponse` y `Content-Disposition: attachment`. El navegador descarga sin navegar, así que `pageshow`, que es lo que reactiva los botones en `initBloqueoEnvio()` (`index.js`), no llega: con `data-bloquear-envio` tal cual, el botón quedaría bloqueado hasta recargar.
- **Opciones:** no bloquear (un doble clic generaría dos `mysqldump` en serie y dos archivos en `backups/`, con disco escaso, regla 11) o bloquear y desbloquear tras un tiempo.
- **Decisión:** bloquear con «Generando…» y desbloquear a los **10 s** con un atributo opcional y genérico, `data-desbloquear-ms`. Evita el doble clic inmediato, que es el caso real, y no deja el botón muerto. Si el `mysqldump` tarda más de 10 s, un segundo clic encola otro respaldo, igual que hoy; no es peor que el estado actual.
- **Comprobación pendiente del desarrollador:** en la réplica, con un `mysqldump` de más de 2 s, que el archivo llegue completo, que el botón muestre «Generando…» y se reactive a los 10 s y que la página no se recargue sola. El agente no tiene la réplica ni puede ver una descarga real.

## Criterio de término

| Criterio | Estado |
| :------- | :----- |
| Suite con `expected failures=4` y número real | Cumplido (282) |
| R6a, R6b, R6c, R7, R19 en verde sin marca | Cumplido |
| Ninguna de las cuatro vistas escribe con GET; sin `href` a esas acciones | Cumplido (pruebas y búsqueda en plantillas; el único `location.reload` que queda es el de `errors/500.html`, ajeno) |
| `respaldar_bd.html` sin `location.reload` | Cumplido |
| Respaldo de más de 2 s llega completo en la réplica | Pendiente del desarrollador |
| `check` y `makemigrations --check --dry-run` | Cumplido |
| Revisión manual en escritorio, 360 px y teclado | Pendiente del desarrollador |
| Respaldo real en producción (cierra AUD-03-002) | Pendiente del desarrollador |

## No verificado

- Nada de JavaScript tiene pruebas automáticas: el modal, `requestSubmit()` y el desbloqueo a los 10 s se ven solo en la revisión manual.
- El modal no cierra con Escape ni mueve el foco al abrirse (no estaba en el alcance); la revisión manual dirá si el teclado basta con Tab y «Cancelar».
- Producción: nada.

## Despliegue

Pasos exactos, día 0 y retroceso a `v14.1-pagos` en la iteración. Sin respaldo previo obligatorio. **Con `collectstatic`** y Ctrl+F5 del cliente. La 04-10 va justo después, en commit separado.
