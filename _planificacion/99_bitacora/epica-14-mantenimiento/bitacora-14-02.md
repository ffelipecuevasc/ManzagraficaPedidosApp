# Bitácora 14-02 · Ejecución en local

- **Fecha:** 2026-11-19
- **Iteración:** [14-02 · Copiar los ítems al duplicar un pedido](../../10_epicas/epica-14-mantenimiento/iteracion-14-02-copiar-items-al-duplicar.md)
- **Estado resultante:** Implementada, pendiente de revisión manual y despliegue.
- **Base:** `main` en `b1427bf`.
- **Hallazgos:** AUD-05-012 pasa a **corregido en código, pendiente de verificar en producción**. Sin hallazgos nuevos; una contradicción con `DESIGN.md` (sección «Contradicciones»).
- **Decisiones (desarrollador, 2026-11-19):** D1 precio unitario del original; D2 nada especial (producto protegido contra borrado); D3 se conserva `valor_venta`; D4 nueva, reemplaza a la propuesta B: página intermedia que pide la fecha de entrega, obligatoria, vacía al abrir y desde mañana (respuesta f del cliente).

## Archivos modificados

- `pedidos/views.py`: `duplicar_pedido` acepta GET (muestra la página) y POST (valida y crea). Pedido e ítems (`bulk_create`) en un solo `transaction.atomic()`; evento `pedido_duplicado` con `on_commit`, como antes. Importa `require_http_methods` y `ReabrirPedidoForm`.
- `pedidos/forms.py` (CRLF): `FechaDesdeMananaValidator` (reutilizable, solo se aplica aquí) y `ReabrirPedidoForm`.
- `pedidos/templates/pedidos/pedido_duplicar.html` (nueva, CRLF): patrón de `pedido_confirm_delete.html`, en azul (color del botón «Reabrir»); `label`, texto de ayuda, `role="alert"` con `aria-describedby` y `aria-invalid`, `min` del navegador y `data-bloquear-envio`.
- `pedidos/templates/pedidos/pedido_detail.html` (CRLF): «Reabrir Pedido» pasa de formulario POST con `data-confirm` a enlace a la página.
- Pruebas: `test_duplicar_items.py` (nueva, 18), `ayudas.py`, `test_pedidos.py`, `test_regresiones.py` (CRLF), `test_acceso.py`, `test_mutaciones_post.py` y `test_eventos_negocio.py`.
- Documentos: la iteración, `registro-pendientes.md` (CRLF), `auditoria-tecnica.md`, `definicion-epica-14.md` y esta bitácora.
- **Sin** `models.py`, migraciones, configuración, dependencias ni estáticos. Tailwind se carga del CDN en tiempo de ejecución (`base.html:16`), así que las clases nuevas no exigen compilar ni `collectstatic`.

## Pruebas

- **Línea base:** `python manage.py test pedidos` → `Ran 298 tests`, `OK (expected failures=4)`.
- **Pruebas nuevas contra el código anterior:** 13 de 18 fallaron por los motivos esperados (sin ítems copiados, fecha copiada del original, GET 405 en vez de la página, sin `atomic()`, validador inexistente). Las 5 restantes fijan lo que ya se cumplía y debe seguir igual: sin pagos y `PENDIENTE`, pedido sin ítems, un solo evento, anónimo al acceso y tope de consultas.
- **Después:** `Ran 316 tests`, `OK (expected failures=4)` (298 + 18).
- `python manage.py check`: sin problemas. `python manage.py makemigrations --check --dry-run`: `No changes detected` (sin migración, nada que clasificar).

### Pruebas existentes que cambiaron (excepción a la 04-01, como P1)

La 04-01 dejó `duplicar_pedido` solo por POST. Con D4 el GET muestra una página de confirmación, igual que P1 hizo con `eliminar_pago`. La propiedad de fondo («un GET nunca escribe», regla 8.5) se mantiene y se prueba.

| Prueba | Antes | Ahora | Por qué |
| :----- | :---- | :---- | :------ |
| `ayudas.duplicar` | POST sin datos | POST con `datos_reabrir()` (mañana en Chile) | El POST exige la fecha; todas las pruebas que duplican pasan por aquí. |
| R6b `test_regresiones.test_r6_duplicar_pedido_rechaza_get` | GET → 405 y 1 pedido | Renombrada `test_r6_duplicar_pedido_get_no_escribe`: GET → 200 y 1 pedido | El GET muestra la página; lo que R6b protege (no crear con GET) sigue afirmado. |
| `test_pedidos.DuplicarPedidoTests.test_copia_cabecera_y_redirige_al_nuevo` | `fecha_entrega` copiada | Fecha = la enviada | D4: la fecha la elige quien reabre. |
| `test_pedidos.DuplicarPedidoTests.test_lo_que_no_se_copia` | Sin ítems (`PENDIENTE_CLIENTE`) | Copia el ítem (cantidad y precio) | Respuesta 2 del cliente; es la prueba que AUD-05-012 pedía cambiar. |
| `test_acceso.PkInexistenteTests` | Duplicar en `SOLO_POST_404` | En `CON_404` (GET → 404) | Con GET ya no responde 405 antes de buscar el pedido. |
| `test_mutaciones_post.test_reabrir_es_formulario_post` | Formulario POST en el detalle | Renombrada `test_reabrir_es_enlace_a_la_pagina_de_la_fecha` | El detalle enlaza; el formulario POST está en la página nueva. |
| `test_mutaciones_post.DuplicarPostTests` y `test_eventos_negocio.test_pedido_duplicado` | POST sin datos | POST con la fecha | Igual que `ayudas`. |

`test_mutaciones_post.AnonimoVaAlAccesoTests` sigue sin cambios: un anónimo con GET va al acceso.

## Consultas (regla 8.12; `AGENTS.md`, sección 11)

Medidas con `CaptureQueriesContext` en una prueba temporal (borrada), pedido de 3 ítems:

| Petición | Antes | Después |
| :------- | ----: | ------: |
| Página nueva (GET `/pedido/duplicar/<pk>/`) | 405, 2 | **3** (sesión, usuario y pedido con cliente y cantidad de ítems en una consulta) |
| Comparable: confirmación de eliminar (GET) | 4 | 4 |
| POST de duplicar | 5 | 6 de datos + 2 marcadores `SAVEPOINT` del `atomic()` en la prueba |
| Detalle del pedido | 12 | 12 |

- La página nueva usa **menos** consultas que la de eliminar: no se supera el tope de +1. `PaginaTests.test_consultas_de_la_pagina` fija un máximo de 5.
- En el POST se quita la lectura perezosa del cliente (`select_related`) y se suman la lectura de los ítems y un `bulk_create`: **+1 neto**, independiente del número de ítems. En producción el `atomic()` se traduce en el inicio y la confirmación de la transacción, no en `SAVEPOINT`.

## Contradicciones

- **`DESIGN.md`, línea 101 (documento protegido, no editado).** Dice: «Toda acción irreversible (eliminar, reabrir, restaurar la base) se confirma en un modal que explica la consecuencia antes de ejecutarla.» Con D4, reabrir se confirma en una página, como ya ocurre con eliminar pedido y eliminar pago. **Propuesta para el desarrollador:** cambiar a «… se confirma en un modal o en una página de confirmación que explica la consecuencia antes de ejecutarla. La acción confirmada se envía como formulario POST.» Si no se cambia, `DESIGN.md` describe un comportamiento que ya no existe para reabrir ni para eliminar.
- **Regla «mañana» a medias:** rige al reabrir, todavía no al crear, editar ni convertir (Épica 10). Decisión aceptada en D4; anotado como riesgo en la iteración.
- **`index.js`, rama `CLONAR` (`index.js:368`):** ya no la usa ninguna plantilla. No se quitó, para no tocar estáticos ni forzar `collectstatic` en este despliegue. Se puede retirar en la Épica 8.

## Decisiones de implementación

- **Sin token de envío único (`envio_unico`):** el doble clic lo frena `data-bloquear-envio`; un reenvío del formulario crearía otro pedido, igual que antes de la iteración. Fuera de alcance.
- **«Mañana»:** `timezone.localdate() + 1 día` (regla 8.6). Una prueba congela la hora a las 23:30 de Chile (ya el día siguiente en UTC) para fijar que se usa la fecha local.
- **`min` en el campo:** solo ayuda del navegador; la regla la valida el servidor.
- **La imagen** sigue compartiendo la ruta, sin copiar el archivo (AUD-02-023, fuera de alcance).

## Lo que no hizo el agente

- Refrescar la réplica (paso 0) ni la revisión manual en escritorio, a 360 px y con teclado: las hace el desarrollador.

## Despliegue (lo hace el desarrollador)

1. **Revisión manual en la réplica refrescada** (`replica-local.md`), en escritorio, a 360 px y solo con teclado: desde un pedido `TERMINADO` con varios ítems, «Reabrir Pedido» abre la página; enviar vacía, con la fecha de hoy y con una pasada muestra el error sin crear nada; con mañana crea el pedido con los mismos productos, cantidades y precios, sin pagos, el mismo total y la fecha elegida. Repetir con un pedido sin ítems. Comprobar el foco visible y que «Cancelar» vuelve al detalle.
2. Respaldo de rutina, descargado y verificado (`respaldo.md`).
3. `git diff --stat v4.2-confirmar-eliminar-pedido -- requirements.txt pedidos/migrations PedidosApp/settings.py pedidos/static` **sin salida**: sin `pip`, `migrate` ni `collectstatic`.
4. Commit y etiqueta anotada `v14.2-duplicar-items`; `git push` con la etiqueta.
5. En PythonAnywhere: `git fetch --tags`, `git checkout v14.2-duplicar-items`, `git describe` y **Reload**.
6. **Día 0:** reabrir un **pedido de prueba** con ítems (no uno real), comprobar el detalle del nuevo (ítems, sin pagos, total y fecha) y el evento `pedido_duplicado` en el admin; borrar después los dos pedidos de prueba. `server.log` y `error.log` sin errores nuevos desde el Reload.
7. **Retroceso** (`retroceso.md`, caso 1, sin migraciones): `git checkout v4.2-confirmar-eliminar-pedido` y Reload. Los pedidos reabiertos con ítems mientras tanto son datos válidos; no hay nada que deshacer.

## Criterio de término

- [x] Pruebas de la tabla en verde; suite `OK (expected failures=4)`.
- [x] Sin migración; consultas medidas y anotadas.
- [ ] Revisión manual en la réplica, en escritorio, a 360 px y con teclado.
- [ ] Día 0 en producción y AUD-05-012 verificado.
