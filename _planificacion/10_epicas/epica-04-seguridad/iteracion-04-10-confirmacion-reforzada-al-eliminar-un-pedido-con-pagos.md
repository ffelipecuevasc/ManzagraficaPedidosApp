# Iteración 04-10 · Confirmación reforzada al eliminar un pedido con pagos

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones abiertas). Redactada el 2026-11-17 ([bitacora-04-10-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-10-redaccion.md)). Cuatro decisiones `PENDIENTE_DESARROLLADOR` (sección «Decisiones»), cada una con opción recomendada.
- **Origen:** decisión del desarrollador del 2026-11-17 (dicha por él) sobre la pregunta `PENDIENTE_CLIENTE` «¿se puede eliminar un pedido que tiene pagos?» (registro, sección 2; detectada en la redacción de la 04-06). **El cliente no ha respondido si el borrado es intencional.** Esta iteración **no espera esa respuesta**: informa y pide confirmación, sin cambiar lo que ocurre al borrar. Si el cliente dijera que el borrado **no** es intencional, se replantea (ver «Fuera de alcance»).
- **Subfase del plan:** nueva (revisión de la Épica 04, 2026-11-17); misma clase de riesgo que AUD-02-001 (pérdida de historial), sin ser ese hallazgo.
- **Depende de:** la 04-01 (comparte `views.py` y el patrón de confirmación; ver «Coordinación»). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → … → 04-09 → **04-10**, la última de la Épica 04.
- **RDA relacionadas:** RDA-007; RDA-008 (inventario cerrado de eventos: relevante solo con D1-B); RDA-017 (borrado físico con doble confirmación, **para usuarios**; no se aplica a pedidos, ver «Contradicciones»).
- **Hallazgos que cierra:** ninguno por sí sola; reduce el riesgo de la pregunta `PENDIENTE_CLIENTE`.
- **Cambio de esquema:** **ninguno con D1-A** (recomendada). Con D1-B, una migración de **Clase 1** (`choices` de `RegistroEvento.tipo`): sería la **`0010`**, porque la `0008` es de la 04-06 y la `0009` de la 04-08 (verificado: hoy la última aplicada es la `0007`).
- **Respaldo previo al despliegue:** el de rutina con D1-A; obligatorio con D1-B (hay migración).
- **Archivos que tocará la ejecución:** `pedidos/views.py` (`eliminar_pedido`), `pedidos/templates/pedidos/pedido_confirm_delete.html`, pruebas nuevas, `docs/operacion/` si corresponde, y con D1-B además `pedidos/models.py` y `pedidos/migrations/0010_…` (**consulta previa**, `AGENTS.md`, sección 6). Sin archivos de configuración.

## Objetivo

Que nadie pierda sin darse cuenta los pagos de un pedido: antes de eliminarlo, la pantalla dice cuántos pagos y por qué monto se borrarán junto con él, pide una confirmación explícita, y la eliminación deja un evento con la cantidad de pagos borrados.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main`, con archivo y línea.
- **Dicho por el desarrollador:** no comprobado por el agente.
- **Inferido:** sale de leer el código o del comportamiento documentado de Django; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## Qué hay hoy (verificado)

### La relación y la vista

- `Pago.pedido` es `ForeignKey(Pedido, on_delete=CASCADE, related_name='pagos')` (`models.py:92`): al borrar un pedido, Django borra también sus pagos y sus ítems (`ItemPedido.pedido`, `CASCADE`). `Pago.monto` es un entero en pesos (`models.py:93`, `PositiveIntegerField`).
- `eliminar_pedido` (`views.py:378-385`): `@login_required`; el GET muestra `pedido_confirm_delete.html`; el POST ejecuta `pedido.delete()`, llama a `registrar_evento('pedido_eliminado', …)` y redirige a la lista. **No cuenta los pagos ni los menciona en ningún momento.** La 04-01 ya verificó que esta vista no escribe con GET y la deja como está (`iteracion-04-01`, tabla de rutas).
- **La vista no usa la 03-01:** no está decorada ni captura nada; una excepción llegaría a Django (como el resto, RDA-019).

### La pantalla

- `pedido_confirm_delete.html` dice «Esta acción es permanente y no se puede deshacer. Todos los datos de este trabajo se perderán.» y tiene un formulario POST con el token CSRF y el bloqueo de doble envío de la 03-04 (`data-bloquear-envio="Eliminando…"`). **No dice que existen pagos** ni cuánto suman.
- Formato de montos en el proyecto: el filtro `intcomma` de `humanize` (por ejemplo `${{ pedido.valor_venta|intcomma }}` en `pedido_detail.html:188`), que respeta el separador de miles con punto de `es-cl`.
- `DESIGN.md` pide que las acciones irreversibles se confirmen «en un modal que explica la consecuencia» y se envíen como formulario POST. La confirmación de pedidos, clientes y productos ya es una **página** y no un modal (y la 04-01 crea otra igual para pagos, P1); esta iteración **sigue el patrón vigente** (página con formulario POST) y no lo cambia: ver «Contradicciones».

### El evento

- **Hoy ya existe un evento al eliminar un pedido:** `pedido_eliminado` está en el inventario de `RegistroEvento` (`models.py:254`), se escribe en `views.py:383` con el resumen `Pedido #N eliminado` y lo prueba `test_eventos_negocio.py:62-66`. **No dice cuántos pagos se perdieron.**
- Los eventos son un inventario cerrado (RDA-008; comentario de `models.py:248-250`) y su resumen guarda **solo identificadores**: «nada de nombres, teléfonos, montos ni copias de objetos» (`models.py:276`, `eventos.py`). **Por eso el evento lleva la cantidad de pagos y no el monto**, aunque la pantalla sí muestre el monto.
- `registrar_evento` programa la escritura con `transaction.on_commit` y nunca lanza hacia quien llama (`eventos.py`): si `delete()` falla, no queda evento. Los pagos que se borran **en cascada** no emiten `pago_eliminado` (ese evento es de `eliminar_pago`, `views.py:1585`).

### Datos de producción (medidos el 2026-10-20, `linea-base-produccion.md`)

- 870 pedidos y **1.033 pagos**: unos 1,2 pagos por pedido (aritmética). **No se midió cuántos pedidos tienen al menos un pago** ni cuántos pedidos se han eliminado; es el dato que dimensiona el problema (evidencia previa, paso 2).

### Otros caminos que borran un pedido

- **Admin de Django:** `PedidoAdmin` (`admin.py:11`) usa el borrado por defecto: su pantalla de confirmación enumera los objetos relacionados que se borrarían (inferido de Django; se confirma en la réplica) y **no registra evento** (`senales.py` solo conecta acceso exitoso y fallido). **Fuera de alcance**, igual que antes.
- Borrar un cliente ya no arrastra pedidos con la 04-06 (`PROTECT`): después de ella, `eliminar_pedido` y el admin son los únicos caminos que borran pagos junto con un pedido.

## Contradicciones con la planificación

- **El enunciado pedía «definir el tipo de evento y su migración de Clase 1».** El tipo **ya existe** (`pedido_eliminado`, verificado). Crear otro no es necesario para registrar la cantidad de pagos: basta enriquecer el resumen (D1-A, sin migración). La opción con tipo nuevo y migración `0010` queda como D1-B.
- **RDA-017 («borrado físico con doble confirmación») es para usuarios (Épica 09), no para pedidos.** Esta iteración usa un patrón parecido por analogía, no por esa RDA.
- **`DESIGN.md` habla de modal y las confirmaciones de la aplicación son páginas.** Se mantiene la página; si la Épica 08 las convierte en modales, se actualiza junto con las demás.
- **La 04-06 dice que la pregunta sobre pagos «queda al cliente»**: sigue siendo verdad (el cliente no ha respondido); lo nuevo es que el desarrollador decidió reforzar la confirmación mientras tanto.

## Fuera de alcance

- **Cambiar la cascada** (`Pago.pedido` sigue en `CASCADE`): sin migración de comportamiento y sin tocar `models.py` con D1-A.
- **Anular en vez de borrar** (un estado nuevo): es funcionalidad nueva y exigiría una RDA y la respuesta del cliente.
- **`PROTECT` en `Pago.pedido`:** impediría borrar cualquier pedido con pagos; lo descartó el desarrollador por ahora.
- El borrado desde el admin de Django, y el borrado de **pagos individuales** (`eliminar_pago`, 04-01, evento `pago_eliminado` ya existente).
- Cambiar el borrado de clientes (04-06), de cotizaciones o de productos.
- Mover la confirmación a un modal (Épica 08).

## Alcance

1. **Aviso antes de borrar (GET):** `pedido_confirm_delete.html` muestra, cuando el pedido tiene pagos, **cuántos pagos y qué monto total** se borrarán junto con el pedido (monto con punto de miles, `$15.000`), con el texto de la sección «Textos». Cuando no tiene, lo dice en una línea y la pantalla sigue como hoy.
2. **Confirmación explícita (POST):** con pagos, el servidor **exige** la confirmación de D2 además del botón. Sin ella (falta o incorrecta) no se borra nada: se vuelve a pintar la pantalla con un mensaje claro, sin evento y sin detalles técnicos.
3. **Cifras al confirmar:** el formulario lleva oculta la cantidad de pagos que la persona vio. Si al enviar la cantidad real es otra (se agregó o quitó un pago entre medio), **no se borra**: se repinta la pantalla con las cifras nuevas (D4).
4. **Evento:** el borrado deja un evento con la **cantidad** de pagos borrados (D1), calculada **antes** de `delete()`.
5. **Una sola operación:** el recuento, la comprobación y `delete()` ocurren en el mismo `transaction.atomic()` (regla 8.3); el evento sigue programado con `on_commit`.
6. **Fuera:** lo de la sección anterior.

## Textos (español de Chile, tú; propuesta)

- **Con pagos:** «Este pedido tiene **3 pagos registrados por un total de $45.000**. Si lo eliminas, esos pagos también se borrarán y no se podrán recuperar.» Debajo: «Para confirmar, escribe **ELIMINAR**.»
- **Sin pagos:** «Este pedido no tiene pagos registrados.» (y el aviso actual).
- **Falta o error de confirmación:** «Escribe ELIMINAR para confirmar. No se eliminó nada.»
- **Cambiaron los pagos:** «Mientras tanto cambió la cantidad de pagos de este pedido. Revisa los datos nuevos y confirma otra vez. No se eliminó nada.»
- Singular y plural bien escritos («1 pago», «3 pagos»). El mensaje de error con `role="alert"`, texto de contraste suficiente y foco visible (`DESIGN.md`, sección de accesibilidad); el campo con `label` y `aria-describedby` hacia el aviso. Se revisa a 360 px.

## Evento

- **Hoy:** `pedido_eliminado`, resumen `Pedido #N eliminado`.
- **D1-A (recomendada):** el mismo tipo, con un resumen más completo: `Pedido #N eliminado, con K pagos` o `Pedido #N eliminado, sin pagos`. Solo identificadores y una cantidad. Sin migración, sin cambio de inventario (RDA-008) y sin cambio de crecimiento: **no** se agrega ninguna fila.
- **Qué no se guarda:** el monto, el nombre del cliente ni los pagos. La pantalla los muestra; el registro no los conserva (regla 7.4 y `models.py:276`).
- **Quién:** el usuario autenticado (`request.user`), como hoy.

## Coordinación con las otras iteraciones

- **04-01 (mutaciones solo por POST):** no cambia `eliminar_pedido` (ya cumple: GET muestra, POST borra, `iteracion-04-01`, tabla de rutas) y crea `pago_confirm_delete.html` **copiando** el patrón de `pedido_confirm_delete.html`. La 04-10 parte del estado en que la 04-01 deje esa plantilla y no toca la de pagos. Una prueba existente (`test_bloqueo_envio.py:38`) comprueba el bloqueo de doble envío de esta pantalla: se conserva el atributo `data-bloquear-envio` en el formulario.
- **04-06 (protección del historial):** **no se mezclan.** La 04-06 cambia dos relaciones de `Cliente` y la vista `eliminar_cliente`; esta cambia `eliminar_pedido` y su plantilla. No comparten archivos de modelos, ni migraciones (con D1-A), ni pruebas (R14 sigue siendo de clientes). La 04-06 deja explícito que los pagos en cascada «quedan al cliente»; la 04-10 **no** cambia la cascada.
- **04-08 (acceso y límites):** solo comparte la numeración de migraciones (`0009`); con D1-A no hay migración aquí.
- **04-04 (`RESTAURAR`):** esta iteración **reutiliza el patrón** de escribir una palabra (D2-A). El criterio de comparación (espacios y mayúsculas) debe ser **el mismo** que fije la 04-04.

## Decisiones (`PENDIENTE_DESARROLLADOR`)

**D1 · Tipo de evento.**
- **A (recomendada): el mismo `pedido_eliminado`** con la cantidad de pagos en el resumen. Sin migración; el evento ya existe y está probado.
- **B:** un tipo nuevo, por ejemplo `pedido_eliminado_con_pagos`, para poder filtrarlo en el admin de eventos. Migración de **Clase 1** (`0010`, después de la `0009` de la 04-08; se detiene si `sqlmigrate` muestra cualquier `ALTER`, `AGENTS.md`, regla 8.1), respaldo previo y cambio del inventario cerrado (RDA-008). El mismo dato ya se distingue por el texto del resumen.

**D2 · Forma de la confirmación.**
- **A (recomendada): escribir `ELIMINAR`**, exigido por el servidor, como `RESTAURAR` en la 04-04. Obliga a detenerse; es el patrón que ya existe.
- **B:** una casilla «Entiendo que se borrarán N pagos por $X», exigida por el servidor. Menos fricción, más fácil de marcar sin leer.
- **C:** escribir el **número del pedido**. Evita confundir un pedido con otro, pero no refuerza la lectura del aviso.

**D3 · Cuándo se exige.**
- **A (recomendada): solo cuando el pedido tiene al menos un pago.** Un pedido de prueba sin pagos se elimina como hoy.
- **B:** siempre, aunque no haya pagos. Coherente, pero agrega pasos a un caso sin riesgo financiero.

**D4 · Si cambian los pagos entre mostrar y confirmar.**
- **A (recomendada):** el formulario lleva la cantidad vista y el servidor la compara; si difiere, repinta sin borrar. Con un solo worker la ventana es el tiempo entre abrir la pantalla y enviarla.
- **B:** no comparar: se borra lo que haya al momento de enviar. Más simple; la persona podría perder un pago que no vio.

## Pasos

0. Respaldo de la réplica (`respaldo.md`). Con D1-B, además consulta previa para `makemigrations` y `migrate` en local.
1. Línea base: `test pedidos` (número y fallos esperados tras la 04-09; `showmigrations pedidos`, que con D1-A no cambia).
2. **Evidencia previa (la reúne el desarrollador, en la réplica, solo lectura, solo conteos; no ejecutada ni probada por el agente):** cuántos pedidos tienen al menos un pago y cuántos eventos `pedido_eliminado` existen (la réplica trae los de hasta su último refresco). Sirve para dimensionar y comprobar que la pantalla nueva se verá en un caso frecuente:
   ```sql
   SELECT (SELECT COUNT(*) FROM pedidos_pedido)                                   AS pedidos,
          (SELECT COUNT(DISTINCT pedido_id) FROM pedidos_pago)                    AS pedidos_con_pagos,
          (SELECT COUNT(*) FROM pedidos_registroevento WHERE tipo='pedido_eliminado') AS eliminaciones_registradas;
   ```
   `mysql` exige consulta previa incluso en local (`AGENTS.md`, sección 6). En la bitácora, solo estos tres conteos.
3. Pruebas primero (tabla siguiente); ver fallar las de aviso, confirmación y evento.
4. `eliminar_pedido` (recuento, comprobación, `delete()` en un `transaction.atomic()`, evento) y `pedido_confirm_delete.html` (aviso, campo de confirmación, mensajes, cantidad oculta).
5. Revisión manual en la réplica, escritorio y 360 px: eliminar un pedido **con** pagos (aviso, error por falta de la palabra, error con la palabra mal escrita, borrado correcto), uno **sin** pagos (como hoy), y ver el evento en el admin.
6. Solo D1-B: `makemigrations pedidos --name pedido_eliminado_con_pagos`, **`sqlmigrate pedidos 0010` en la réplica** (esperado, inferido: solo el comentario del `AlterField`, sin SQL) copiado en la bitácora.
7. Bitácora, registro, estado «En revisión»; la pregunta `PENDIENTE_CLIENTE` sigue abierta hasta que el cliente responda.

## Pruebas

| Punto | Prueba |
| :---- | :----- |
| Aviso con pagos (GET) | Un pedido con 2 pagos: 200, la pantalla dice «2 pagos» y el monto total exacto con punto de miles, y trae el campo de confirmación y la cantidad oculta. |
| Aviso sin pagos (GET) | 200, dice que no hay pagos, **sin** campo de confirmación (D3-A). |
| Sin pagos (POST) | Borra el pedido y sus ítems, redirige a la lista, **un** evento `pedido_eliminado` con `sin pagos`. |
| Con pagos y confirmación (POST) | Con `ELIMINAR` y la cantidad vista: el pedido, sus ítems **y sus pagos** se borran (la cascada sigue igual), redirige, **un** evento con `con 2 pagos` y sin monto ni nombre. |
| Falta de confirmación | Con pagos y sin el campo, o vacío, o con otra palabra (`eliminar` según el criterio de la 04-04): 200 con el mensaje, **nada** se borra (pedido, ítems y pagos siguen), **ningún** evento nuevo y sin `str(e)`. |
| Cambio de pagos (D4) | Se muestra con 1 pago; se agrega otro; se envía con `ELIMINAR` y la cantidad vieja: no se borra, la pantalla muestra «2 pagos» y el monto nuevo. |
| Atomicidad | Con `delete()` forzado a fallar (`mock`): ninguna fila cambia y **no** queda evento. |
| Un pedido inexistente | 404 como hoy (`test_acceso`, `PkInexistenteTests`); sin sesión, redirige al acceso. |
| Doble envío | El formulario conserva `data-bloquear-envio` (`test_bloqueo_envio.py:38`). |
| Existentes | `test_eventos_negocio.py:62-66` (con el nuevo resumen si lo comprueba), `test_acceso`, `test_regresiones` y la suite completa con los fallos esperados heredados. |
| Solo con D1-B | `makemigrations --check --dry-run` sin cambios tras crear `0010`; el tipo nuevo aparece en el admin de eventos. |

## Verificación en producción (la hace el desarrollador; todo **no verificado** hasta entonces)

1. Respaldo previo, descargado y verificado (`respaldo.md`) por rutina; con D1-B, `migrate` y `showmigrations pedidos` antes del Reload.
2. Tras el Reload, abrir la pantalla de eliminar de un pedido **con pagos** y ver el aviso con las cifras **sin enviar el formulario**. **No se elimina un pedido real para probar.**
3. `server.log` sin errores nuevos.
- **No verificado:** cuántos pedidos de producción tienen pagos y cuántos se han eliminado desde el despliegue de eventos; si el cliente elimina pedidos con pagos a propósito (la pregunta sigue abierta).

## Plan de retroceso

- **Con D1-A:** `retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y Reload. Los eventos escritos con el resumen nuevo permanecen y son inofensivos.
- **Con D1-B:** caso 2: `migrate pedidos 0009` (revierte la `0010`; sin SQL, inferido), luego la etiqueta y Reload; primero la migración, después el código. Los eventos del tipo nuevo ya escritos permanecen (el tipo no se valida en la base).
- No hay datos que deshacer: la iteración no cambia qué se borra, solo lo que se pide antes.

## Criterio de término

- Tabla de pruebas en verde; resto de la suite sin cambios.
- Revisión manual en la réplica hecha (con y sin pagos, 360 px).
- Con D1-B, `sqlmigrate pedidos 0010` sin SQL copiado en la bitácora.
- Verificación 2 de producción hecha.
- La pregunta `PENDIENTE_CLIENTE` sigue registrada (no la cierra esta iteración).

## Riesgos

- **Confirmación por costumbre:** quien elimina con frecuencia aprende a escribir la palabra sin leer el aviso. Mitigado porque solo se exige cuando hay pagos y el aviso dice la cifra.
- **No protege el historial:** los pagos se siguen borrando; la iteración solo informa, pide confirmación y deja rastro. Si el cliente dice que el borrado no es intencional, hay que replantear (`PROTECT` o anular), que es una iteración aparte.
- **El evento no guarda el monto:** si se pierde un pago por error, el registro dice cuántos pagos eran, no cuánto sumaban (es la regla del registro). El respaldo diario es la única recuperación.
- **Admin de Django sin aviso propio ni evento:** quien borre desde el admin sigue sin dejar rastro (fuera de alcance).
- **Dos pantallas de confirmación con criterios distintos** (`RESTAURAR` y `ELIMINAR`): se alinea el criterio de comparación con la 04-04.
- **Cambiar el resumen de un evento existente (D1-A):** si alguna prueba o informe lee el texto exacto, se ajusta al ejecutar; no se encontró ninguno (el `test_pedido_eliminado` comprueba tipo y entidad).
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-09.
