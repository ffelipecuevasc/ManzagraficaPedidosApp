# Iteración 04-01 · Mutaciones solo por POST

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** **Implementada, pendiente de revisión manual y despliegue** (2026-11-18; [bitacora-04-01](../../99_bitacora/epica-04-seguridad/bitacora-04-01.md)). No está Terminada: faltan la revisión manual en la réplica, el despliegue y el día 0. Antes: Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-01-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-01-redaccion.md)) con las decisiones (a) y (b) del desarrollador del 2026-11-17. P1 y P2 **resueltos el 2026-11-17** por el desarrollador (dicho por él; [bitacora-04-01-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-01-cierre.md)): P1, se crea `pago_confirm_delete.html` y R7 queda como está; P2, el panel queda en la 06-01. Etiqueta `v4.1-mutaciones-post` fijada el 2026-11-17; ~~la fecha se fija al cerrar la vigilancia de la 03-05~~ (superado el 2026-11-18, RDA-021: la fija el desarrollador, después de la 14-01).
- **Subfase del plan:** 4.1 «Mutaciones solo por POST» (`plan-de-trabajo.md`, FASE 4).
- **Depende de:** Épica 02 (Terminada). Se redactó en paralelo a la vigilancia de la 03-05; ~~**ni se ejecuta en local ni se despliega hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17) (desde el lunes 2026-11-23 a las 23:48:12, nota del 2026-11-17 en `definicion-epica-04.md`)~~ **superado el 2026-11-18 (RDA-021): no hay vigilancia que cerrar y puede ejecutarse. Se despliega después de la 14-01** (arreglo urgente de pagos, RDA-022, que va antes; **esta iteración no suma AUD-05-010 ni AUD-05-011**, decisión del desarrollador del 2026-11-18).
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-013 (errores con `logging`), RDA-019 (errores de vista los maneja Django; la captura va fuera del `atomic`).
- **Hallazgos que cierra:** AUD-02-002 (eliminar pago da 500), AUD-02-006 en su parte de GET (la parte del mensaje la cerraron la 01-09 y la 03-04), AUD-02-028 (duplicado sin autor), AUD-03-002 (recarga a los 2 s del respaldo; el cierre exige la comprobación en producción).
- **Regresiones que pasan a verde:** R6a, R6b, R6c, R7 y R19.
- **Cambio de esquema:** ninguno. No hay migración.
- **Respaldo previo al despliegue:** no lo exige por sí misma (sin migraciones). Se sigue el protocolo normal de `docs/operacion/despliegue.md`.
- **Etiqueta y ventana:** despliegue propio, el primero de la Épica 04 (orden 04-01, **04-10**, 04-02, 04-03 y siguientes, decisión del 2026-11-17). **Etiqueta `v4.1-mutaciones-post`** (decisión del desarrollador, 2026-11-17). ~~La fecha se fija al cerrar la vigilancia de la 03-05: no antes del lunes 2026-11-23 a las 23:48:12.~~ **Superado el 2026-11-18 (RDA-021):** la fecha la fija el desarrollador, **después del despliegue de la 14-01**. El destino de retroceso de esta iteración pasa a ser la etiqueta de la 14-01, **`v14.1-pagos`** (desplegada y verificada el 2026-11-18, dicho por el desarrollador), porque es la que está en producción (`despliegue.md`, sección 1).
- **Coordinación con la 04-10 (decisión del desarrollador, 2026-11-17):** la 04-10 se despliega **justo después** de esta y edita `eliminar_pedido` y `pedido_confirm_delete.html`. Esta iteración **copia** el patrón vigente de esa plantilla para `pago_confirm_delete.html` (punto 4 del alcance) y no toca `eliminar_pedido`; van en commits separados y en ese orden, así que no se pisan.

## Objetivo

Que ninguna petición GET cree, modifique o elimine datos ni ejecute procesos (`AGENTS.md`, regla 8.5), que eliminar un pago vuelva a funcionar con confirmación, que el respaldo generado desde la web llegue al equipo del usuario y que el pedido duplicado quede con el usuario que lo duplicó.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main` (`253a9c2`); se cita archivo y línea.
- **Dicho por el desarrollador:** decisiones o datos que el agente no puede comprobar; se marca así.
- **Inferido:** sale de leer el código, no de ejecutarlo. Se marca «(inferido)» y se dice cómo se confirma.

## Problema (verificado en el repo)

| Ruta (`pedidos/urls.py`) | Vista | Qué hace con GET | Evidencia |
| :----------------------- | :---- | :--------------- | :-------- |
| `pedido/<pk>/cambiar/<estado>/` (`:16`) | `cambiar_estado_pedido` | Guarda el estado y registra el evento, sin mirar el método. | `views.py:392-407`; enlaces `<a href>` en `pedido_detail.html:66` y `:73` |
| `pedido/duplicar/<pk>/` (`:17`) | `duplicar_pedido` | Crea un pedido nuevo con `creado_por` nulo (no se asigna). | `views.py:481-503`; botón `data-confirm` en `pedido_detail.html:80-87` |
| `base_datos/respaldar_bd/accion/` (`:47`) | `generar_respaldo_bd` | Ejecuta `mysqldump`, escribe en `backups/` y descarga. | `views.py:1219-1238`; enlace en `respaldar_bd.html:18` con `onclick="setTimeout(function(){ location.reload(); }, 2000);"` en `:19` |
| `pagos/eliminar/<pk>/` (`:57`) | `eliminar_pago` | Con GET renderiza `pedidos/pago_confirm_delete.html`, que no existe: 500. Con POST borra dentro de un `atomic` (03-03). | `views.py:1568-1591`; la plantilla no está en `pedidos/templates/pedidos/`; enlaces GET en `pedido_detail.html:343` y `pago_list.html:108` |

Cómo funciona hoy la confirmación con `data-confirm` (verificado): `initDetailModals()` (`index.js:348-385`) intercepta el clic, copia `data-url` en `btnConfirmar.href` y muestra `#modal-confirmacion`. El botón «Confirmar» del modal es un **enlace** (`pedido_detail.html`, `<a id="modal-btn-confirmar" href="#">`, cerca de `:390`): confirmar hace una **navegación GET**. El modal solo existe en `pedido_detail.html` (`:365`) y solo conoce el tipo `CLONAR`.

### Revisión del resto de `urls.py` (decisión b)

Se revisaron las 41 rutas de `pedidos/urls.py` y todas las escrituras de `views.py` (búsqueda de `.save(`, `.create(`, `.delete(`, `registrar_evento`).

| Ruta o vista | ¿Escribe con GET? | Evidencia |
| :----------- | :---------------- | :-------- |
| `eliminar_pedido` | No. GET muestra la confirmación; borra solo dentro de `if request.method == 'POST'`. | `views.py:378-385` |
| `eliminar_cliente` | No. Igual patrón. | `views.py:689-696` |
| `eliminar_cotizacion` | No. Igual patrón. | `views.py:945-951` |
| `eliminar_producto` | No. Igual patrón, con `ProtectedError`. | `views.py:1121-1138` |
| `convertir_a_pedido`, `restaurar_bd`, `ingresar_pago`, `editar_pago`, `crear_*`, `editar_*` | No: escriben solo bajo `request.method == 'POST'`. | `views.py:954-1017`, `:1242-1293`, `:1481-1560` y vistas de formularios |
| `api_crear_cliente_rapido`, `api_crear_producto_rapido` | No: ya tienen `@require_POST`. | `views.py:698-700`, `:1145-1147` |
| `estadisticas_bd`, `exportar_cotizacion_pdf`, listados y detalles | No escriben (lectura). `test_acceso.BaseDeDatosPermisosTests` ya afirma que `estadisticas_bd` no escribió `HistorialBD` para un usuario común. | `views.py:1318-1360`, `:1036-1066` |
| **`dashboard` (`''`)** | **Sí.** Llama a `registrar_metricas_diarias()` (`views.py:73`), que inserta en `HistorialBD` una vez al día (`utils.py:196`). | AUD-01-006; asignado a la 06-01 y a la orden de mantención diaria (RDA-009) |

**Resultado:** fuera de las cuatro rutas del alcance, la única escritura con GET es la del panel. Las cuatro vistas de eliminar no se suman al alcance porque ya escriben solo con POST; sus enlaces GET llevan a una página de confirmación que no escribe, y eso cumple la regla 8.5. El panel queda fuera por P2 (resuelto: 06-01).

## Alcance

1. **`cambiar_estado_pedido` solo POST.** `@require_POST` debajo de `@login_required`. En `pedido_detail.html:66` y `:73`, los dos enlaces pasan a formularios POST con `{% csrf_token %}` y `data-bloquear-envio`. Sin confirmación: hoy no la tiene y cambiar de estado no destruye nada (inferido; se ve en la revisión manual).
2. **`duplicar_pedido` solo POST y con autor.** `@require_POST`; el pedido nuevo lleva `creado_por=request.user` (AUD-02-028, decisión del desarrollador del 2026-11-04). El botón «Reabrir Pedido» queda dentro de un formulario POST y conserva `data-confirm` (decisión a). No cambia qué se copia: ~~la pregunta `PENDIENTE_CLIENTE` sigue aparte~~ **Respondida el 2026-11-18 (respuesta 2 del cliente, dicha por el desarrollador): al duplicar se copian los ítems y no los pagos;** el cambio se propone para la Épica 14 y no entra en esta iteración.
3. **`generar_respaldo_bd` solo POST.** `@require_POST` como decorador **más interno**, debajo de `@login_required` y `@user_passes_test` (ver «Pruebas de la 02-05»). El enlace de `respaldar_bd.html:18-19` pasa a formulario POST y **se retira el `onclick` con `location.reload()`** (AUD-03-002). Para que la lista de respaldos se actualice, el usuario recarga a mano o vuelve a entrar; no se agrega otra recarga automática.
4. **`eliminar_pago` con página de confirmación (P1, excepción a la decisión a).** Se **crea** `pedidos/templates/pedidos/pago_confirm_delete.html` con el mismo patrón que las otras tres de eliminar (`pedido_confirm_delete.html`, formulario POST con `{% csrf_token %}` y `data-bloquear-envio="Eliminando…"`, `:34`). GET muestra la confirmación (200) y no escribe; POST borra con la lógica de la 03-03, que no se toca. La vista no lleva `@require_POST`: ya escribe solo bajo `request.method == 'POST'` (`views.py:1577`). Los dos enlaces (`pedido_detail.html:343`, `pago_list.html:108`) siguen siendo enlaces GET hacia la confirmación, como los de eliminar pedido.
5. **Confirmación reutilizada (decisión a) para duplicar.** `initDetailModals()` cambia para que «Confirmar» envíe el formulario que contiene el disparador (`form.requestSubmit()` o equivalente) en vez de navegar a `data-url`. El modal sigue solo en `pedido_detail.html`, que es donde está «Reabrir Pedido». No se crean plantillas de confirmación aparte de la de P1. Este cambio es de `index.js` pero **no toca el contrato de la API** (`AGENTS.md`, sección 9): solo cambia el modal.
6. **Pruebas que fijaban el GET** se actualizan en la misma iteración (sección «Pruebas»).

## Decisiones del desarrollador (2026-11-17, dichas por él)

- **(a)** La confirmación reutiliza el mecanismo existente (`data-confirm`) dentro de un formulario POST, sin plantillas de confirmación nuevas. Vigente para cambiar estado, duplicar y respaldo; P1 es su única excepción.
- **(b)** Toda otra ruta que mute datos con GET se corrige en esta iteración. Resultado de la revisión: solo el panel; P2 es su única excepción.
- **Anterior (2026-11-04):** la 04-01 asigna `creado_por = request.user` al duplicar; R19 pasa a verde aquí.

## Puntos resueltos (2026-11-17, decisión del desarrollador, dicha por él)

**P1 · Eliminar pago: se crea la página de confirmación.** R7 (`test_regresiones.py:239-247`) exigía GET 200 y chocaba con la decisión (a). Resuelto con la opción B: se crea `pago_confirm_delete.html`; GET muestra la confirmación (200) y POST borra. **R7 se mantiene sin cambios** y pasa a verde. Es la única excepción a la decisión (a). Queda descartado reescribir R7 a 405.

**P2 · El panel escribe `HistorialBD` con GET (`views.py:73`).** Resuelto con la opción A: se deja en la 06-01, que lo lleva a la orden de mantención diaria (RDA-009). Motivo: corregirlo aquí mezclaría dos fases en un despliegue (RDA-007). Es la única excepción a la decisión (b).

## Reutilización de la 03-04

| Pieza | Dónde aplica | Por qué |
| :---- | :----------- | :------ |
| `data-bloquear-envio` (`index.js:808-870`) | Formularios de cambiar estado, duplicar y el de `pago_confirm_delete.html`. | Un doble clic repetiría la acción (dos duplicados, dos cambios de estado). `DESIGN.md` 5.1 exige deshabilitar el botón. |
| `data-bloquear-envio` en el respaldo | **No tal cual.** | La respuesta es una descarga (`Content-Disposition: attachment`): la página no navega, `pageshow` no se dispara y el botón quedaría bloqueado (inferido de `index.js:860-865`). Opciones: desbloquear tras un tiempo prudente o no bloquear. Se decide en la ejecución mirando la descarga real en la réplica; se anota en la bitácora. |
| Token de envío (`pedidos/envio_unico.py`) | **No aplica.** | Está hecho para formularios de creación con campo oculto emitido al abrirlos (`pedido`, `cotizacion`, `pago`). Duplicar sale de un botón en el detalle; con un worker las peticiones van en serie y el bloqueo del botón cubre el doble clic (inferido). Extenderlo exigiría emitir tokens en el detalle (+consultas por página, `AGENTS.md` sección 11). |
| Aviso de error (`base.html`, 03-04) | Respaldo fallido. | La vista ya hace `messages.error` y redirige a `respaldar_bd`, y `test_contrato_error.MensajesDeErrorSeVenTests` prueba que se ve. Con POST el flujo es el mismo. |

## Pasos

0. Línea base: `python manage.py test pedidos` (esperado: 267 pruebas, `OK (expected failures=9)`, dato de la 03-04; se vuelve a medir).
1. **Pruebas primero.** Cambiar `ayudas.cambiar_estado` y `ayudas.duplicar` a POST (`ayudas.py:32-39`). Escribir las pruebas nuevas (sección siguiente) y verlas fallar.
2. `cambiar_estado_pedido` y su plantilla.
3. `duplicar_pedido` (POST y `creado_por`) y su botón.
4. Modal: `initDetailModals()` envía el formulario en vez de navegar.
5. `pago_confirm_delete.html` (P1) con el patrón de `pedido_confirm_delete.html`; quitar la marca de R7 y verla en verde.
6. `generar_respaldo_bd` y `respaldar_bd.html` sin recarga.
7. Actualizar las pruebas existentes que usaban GET (lista abajo); quitar `@expectedFailure` de R6a, R6b, R6c, R7 y R19 y actualizar el encabezado de `test_regresiones.py` (`:8-9`).
8. Verificación de `AGENTS.md`, sección 10.5: pruebas, `check`, `makemigrations --check --dry-run` (sin cambios).
9. Revisión manual en la réplica, escritorio y 360 px: los cuatro botones, el modal con teclado (foco visible, Escape o Cancelar), la descarga del respaldo con un `mysqldump` lento (más de 2 s) y que el archivo quede en el equipo.
10. Bitácora, registro y estado «En revisión».

## Pruebas

**Por escribir (fallan antes de la corrección):**
- POST a cambiar estado cambia el estado; GET responde 405 sin cambiarlo (R6a ya lo cubre).
- POST a duplicar crea un pedido con `creado_por` igual al usuario (R19 pasa a POST por la ayuda).
- GET a eliminar pago responde 200 con la confirmación y no borra (R7, sin cambios); POST borra y recalcula (ya lo cubren `test_eventos_negocio.py:104` y `test_fronteras_transaccionales.py:275-326`).
- POST a generar respaldo descarga (ya existe en `test_acceso.py:220`); GET responde 405 sin llamar a `generar_respaldo_mysql` (R6c).
- Las plantillas tocadas contienen `method="post"` y `csrf_token` en esas acciones, y `respaldar_bd.html` ya no contiene `location.reload`.
- Un usuario anónimo que hace GET a las tres rutas con `@require_POST` va al acceso (302), no recibe 405.

**Existentes que cambian (verificado por búsqueda):**

| Prueba | Hoy | Cambio |
| :----- | :-- | :----- |
| `ayudas.cambiar_estado`, `ayudas.duplicar` (`ayudas.py:32-39`) | GET | POST (lo previó la 02-03) |
| `test_eventos_negocio.py:71`, `:77`, `:78`, `:83`, `:146` | GET | POST |
| `test_capturas_amplias.py:49`, `test_contrato_error.py:36` | GET al respaldo | POST |
| `test_pedidos.py:315` | GET a pk inexistente, 404 | POST, 404 (con GET daría 405) |
| `test_acceso.PkInexistenteTests` (`:272`, `:280`) y R20 (`test_regresiones.py:441-447`, usa la misma lista) | GET de cambiar y duplicar a pk inexistente, 404 | Con `@require_POST` el GET da 405 antes de buscar el objeto: esas dos rutas pasan a probarse con POST. Con P1, `GET /pagos/eliminar/<pk inexistente>/` responde 404 (inferido: `get_object_or_404` va antes del `render`), así que `eliminar_pago` puede dejar de ser excepción (`:277`, `:301-303`) y sumarse a la lista con GET; se decide al ejecutar y se anota. |
| `test_errores.test_regresion_eliminar_pago_deja_tipo_y_traza` (`:82-95`) | Afirma el 500 por la plantilla inexistente, «mientras exista» | Con P1 la plantilla existe y el GET da 200: esta prueba **falla** y se retira. La propiedad que cuidaba (traza completa en el registro) ya la cubren las otras pruebas de `test_errores.py`. Se anota en la bitácora. |
| `test_registro.py:24` | `RequestFactory` | Sin cambio (no pasa por la vista). |

**Pruebas de la 02-05 que fijan 302 (`test_acceso`):** no cambian **si el orden de decoradores es** `@login_required`, luego `@user_passes_test` (en respaldo), luego `@require_POST`. Así un anónimo o un usuario común siguen recibiendo 302 al acceso con GET y con POST (`PostAnonimoTests`, `BaseDeDatosPermisosTests`, `:154-221`). Si `@require_POST` quedara por fuera, esas pruebas darían 405 y fallarían: es la forma de comprobar el orden. Los puntos JSON (`PuntosJsonTests`) no se tocan.

**Contrato de `index.js`:** el contrato de la API (sección 9) no cambia. Cambia el comportamiento interno del modal (`initDetailModals`), sin pruebas automáticas de JavaScript en el repositorio: se verifica en la revisión manual.

## Criterio de término

- `python manage.py test pedidos` en verde con **expected failures=4** (quedan R8, R9, R14 y R15). El total de pruebas cambia (267 más las nuevas, menos la retirada de `test_errores`): se anota el número real.
- R6a, R6b, R6c, R7 (sin cambios en su afirmación) y R19 sin `@expectedFailure` y en verde.
- Ninguna de las cuatro vistas escribe con GET; búsqueda en plantillas sin enlaces `href` a cambiar estado, duplicar y generar respaldo. Los enlaces a eliminar pago llevan a `pago_confirm_delete.html`, que responde 200.
- `respaldar_bd.html` sin `location.reload`; en la réplica, un respaldo de más de 2 s llega completo al equipo.
- `check` sin errores y `makemigrations --check --dry-run` sin cambios.
- Revisión manual hecha en escritorio y 360 px.
- **Después del despliegue (lo hace el desarrollador):** un respaldo generado desde la web en producción llega al equipo (criterio de la épica); AUD-03-002 pasa a Resuelto solo con esa comprobación.

## Ejecución (2026-11-18; detalle en la bitácora)

| Criterio de término | Estado |
| :------------------ | :----- |
| Suite en verde con `expected failures=4` (R8, R9, R14, R15); número real | **Cumplido:** 282 pruebas, `OK (expected failures=4)` (línea base: 273, `OK (expected failures=9)`) |
| R6a, R6b, R6c, R7 (sin cambios en su afirmación) y R19 sin `@expectedFailure` y en verde | **Cumplido** |
| Ninguna de las cuatro vistas escribe con GET; sin `href` a cambiar estado, duplicar ni generar respaldo; eliminar pago lleva a una confirmación que responde 200 | **Cumplido** (pruebas y búsqueda en `pedidos/templates`) |
| `respaldar_bd.html` sin `location.reload` | **Cumplido** |
| En la réplica, un respaldo de más de 2 s llega completo al equipo | **Pendiente del desarrollador** (el agente no tiene la réplica) |
| `check` sin errores y `makemigrations --check --dry-run` sin cambios | **Cumplido** |
| Revisión manual en escritorio, a 360 px y con teclado | **Pendiente del desarrollador** |
| Después del despliegue: respaldo real desde la web en producción llega al equipo (cierra AUD-03-002) | **Pendiente del desarrollador** |

**Decisiones de la ejecución:**
- **Respaldo:** el botón se bloquea («Generando…») y se **desbloquea a los 10 s** (`data-desbloquear-ms="10000"`, atributo nuevo y genérico de `initBloqueoEnvio`). Motivo en la bitácora.
- **`PkInexistenteTests`:** cambiar estado y duplicar pasan a `SOLO_POST_404` (se prueban con POST); `eliminar_pago` entra en la lista de GET (responde 404) y deja de ser excepción. La lista de R20 sigue con 12 rutas.
- **`test_errores.test_regresion_eliminar_pago_deja_tipo_y_traza`:** retirada.
- **`test_pedidos.test_lo_que_no_se_copia`:** su afirmación `creado_por` nulo pasa a `creado_por` = quien duplica (AUD-02-028); lo que se copia no cambia.
- **Botón «Confirmar» del modal:** pasa de `<a href="#">` a `<button type="button">`; envía el formulario con `requestSubmit()`.

## Despliegue paso a paso (lo hace el desarrollador; RDA-007 y RDA-021)

1. **[PC · réplica]** Revisión manual en escritorio, a 360 px y con teclado: (a) «Iniciar Pedido» y «Terminar pedido» cambian el estado y bloquean el botón; (b) «Reabrir Pedido» abre el modal, «Cancelar» lo cierra sin crear nada, «Confirmar» crea el duplicado con su usuario como autor; foco visible en los botones del modal; (c) eliminar un pago desde el detalle y desde la lista: confirmación, «Cancelar» y «Sí, Eliminar»; (d) «Generar Nuevo Respaldo BD» con un `mysqldump` de más de 2 s: el archivo llega completo, el botón muestra «Generando…» y se reactiva a los 10 s, la página no se recarga sola.
2. **[PC]** Commit **solo de la 04-01** en `main` (la 04-10 va en otro commit, después). Lista de `despliegue.md`, sección 2: `python manage.py test pedidos` → 282 pruebas, `OK (expected failures=4)`; `check --deploy` con las advertencias conocidas; `makemigrations --check --dry-run` → `No changes detected`.
3. **[PC]** Etiqueta anotada: `git tag -a v4.1-mutaciones-post -m "Iteración 04-01: mutaciones solo por POST"`, `git push origin v4.1-mutaciones-post`, `git ls-remote --tags origin v4.1-mutaciones-post`.
4. **[PC]** `git diff --stat v14.1-pagos v4.1-mutaciones-post -- requirements.txt pedidos/migrations PedidosApp/settings.py` **sin salida**. `git diff --stat v14.1-pagos v4.1-mutaciones-post -- pedidos/static` **debe mostrar solo** `pedidos/static/pedidos/js/index.js`.
5. **[Cliente]** Aviso antes del despliegue y pedido de **Ctrl+F5** después (cambia `index.js` y su URL no lleva versión; con el archivo viejo, «Confirmar» y los enlaces de pestañas abiertas darían 405).
6. **[PA]** `despliegue.md`, sección 3: `git fetch origin --tags`, `git checkout v4.1-mutaciones-post`, `git describe --tags` = `v4.1-mutaciones-post`. **Sin `pip` ni `migrate`. Con `python manage.py collectstatic --noinput`** (1 archivo: `index.js`). `python manage.py check` y **Reload**; se anota la hora de `Starting uWSGI`.
7. **[Navegador, ventana privada, tras Ctrl+F5]** Día 0: pantallas de `despliegue.md`, 3.7; en un pedido de prueba, iniciar y terminar (cambio de estado), reabrir con el modal (el duplicado queda con el usuario), registrar un pago de prueba y eliminarlo por la confirmación; `GET` directo a `/pedido/<pk>/cambiar/EN_PROCESO/` responde 405 sin cambiar nada; **generar un respaldo desde la web y comprobar que llega completo al equipo** (cierra AUD-03-002). Borrar los datos de prueba (pedido original y duplicado).
8. **[PA]** `server.log` desde el reinicio efectivo: sin `nivel=ERROR` nuevos.
9. Fila en `despliegue.md`, sección 5, y cierre de la iteración.

**Retroceso (RDA-021):** `retroceso.md`, caso 1 (sin migraciones): **[PA]** `git checkout v14.1-pagos`, `git describe --tags` = `v14.1-pagos`, **`python manage.py collectstatic --noinput`** (vuelve el `index.js` anterior), `check`, **Reload** y las pantallas de 3.7; Ctrl+F5 en el navegador del cliente. Disparadores: cualquier 500 en detalle de pedido, pagos o respaldos; un botón de cambiar estado, reabrir o eliminar pago que no funciona; el respaldo que no descarga.

**Después:** la 04-10 se ejecuta en local (sin empezar) y se despliega justo después, en commit separado, con retroceso a `v4.1-mutaciones-post`.

## Riesgos

- **Plantilla nueva de confirmación (P1):** debe seguir `DESIGN.md` y extender `pedidos/base.html`, igual que las otras tres; se revisa a 360 px y con teclado.
- **Páginas abiertas al momento del despliegue:** un enlace viejo en una pestaña abierta haría GET y recibiría 405 (página de error de Django, no la propia). Mitigación: el cliente recarga la página tras el despliegue (como el Ctrl+F5 de la 03-05). `PENDIENTE_DESARROLLADOR`: si conviene una plantilla 405 propia (sería otra iteración).
- **Caché del navegador para `index.js`:** si el navegador conserva el `index.js` viejo, «Confirmar» navegaría con GET y daría 405. Mismo remedio (Ctrl+F5); revisar si el archivo lleva versión en la URL.
- **Bloqueo en la descarga del respaldo:** ver la tabla de reutilización.
- **Un despliegue, un propósito (RDA-007):** esta iteración se despliega sola, ~~después de cerrar la vigilancia de la 03-05~~ **después de la 14-01 (2026-11-18, RDA-021 y RDA-022)** y sin mezclar nada de otras iteraciones de la Épica 04, ni el arreglo del panel (P2, 06-01), ni el arreglo de pagos de la 14-01 (AUD-05-010 y AUD-05-011).

## Fuera de alcance

- **Copiar ítems y pagos al duplicar:** ~~pregunta `PENDIENTE_CLIENTE` abierta (`registro-pendientes.md`, sección 2)~~ **Respondida el 2026-11-18 (respuesta 2 del cliente, dicha por el desarrollador): al duplicar se copian los ítems y no los pagos;** el cambio se propone para la Épica 14 y no entra en esta iteración (`registro-pendientes.md`, sección 2). Esta iteración no cambia qué se copia, salvo `creado_por`.
- `registrar_metricas_diarias` en el panel (P2 resuelto: 06-01, RDA-009; motivo RDA-007).
- `eliminar_cotizacion` no registra evento (`views.py:949`), a diferencia de las otras eliminaciones: se anota como propuesta.
- La protección del historial al borrar clientes (04-06, R14).
