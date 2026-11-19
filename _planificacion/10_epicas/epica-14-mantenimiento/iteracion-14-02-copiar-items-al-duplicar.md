# Iteración 14-02 · Copiar los ítems al duplicar un pedido

- **Épica:** 14 · Mantenimiento
- **Estado:** **Pendiente (redactada, decisiones abiertas D1 a D4).** Redactada el 2026-11-19. No se ejecuta hasta que el desarrollador resuelva las decisiones.
- **Origen:** AUD-05-012 (Alta, propuesta). El desarrollador lo vio en el día 0 de la 04-01 (2026-11-18). Respuesta 2 del cliente (2026-11-18, dicha por el desarrollador): **al duplicar se copian los ítems, no los pagos.**
- **Subfase del plan:** ninguna (RDA-022: una Alta va en una iteración propia de la Épica 14).
- **Numeración:** el número 14-02 se reasignó el 2026-11-18 por decisión del desarrollador. Es la segunda excepción explícita a la RDA-022, punto 4. El 14-03 sigue sin reasignarse.
- **Depende de:** la 04-01 (deja `duplicar_pedido` solo por POST y con `creado_por` de quien duplica) y la 04-10 (destino de retroceso). Las dos están Terminadas.
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-008 (inventario cerrado de eventos: no cambia), RDA-021 (sin esperas) y RDA-022 (gravedad y destino).
- **Hallazgos que cierra:** AUD-05-012.
- **Cambio de esquema:** **ninguno**. Sin `models.py` ni migraciones (verificado: `ItemPedido` ya tiene todo lo que hace falta copiar).
- **Respaldo previo al despliegue:** el de rutina. La iteración no cambia el esquema ni los datos que ya existen; solo crea filas nuevas al duplicar.
- **Etiqueta y retroceso:** despliegue propio. Etiqueta propuesta **`v14.2-duplicar-items`** (formato de `despliegue.md`, sección 1; `PENDIENTE_DESARROLLADOR`). Destino de retroceso: **`v4.2-confirmar-eliminar-pedido`**.
- **Archivos que tocará la ejecución:** `pedidos/views.py` (`duplicar_pedido`) y pruebas (`pedidos/tests/test_pedidos.py`, `DuplicarPedidoTests`, y pruebas nuevas). Según D4, quizás `pedido_detail.html` (un mensaje). **Sin** `models.py`, migraciones, configuración ni estáticos.

## Objetivo

Que «Reabrir Pedido» cree un pedido nuevo con el mismo detalle de productos que el original, sin copiar sus pagos, y que la copia sea completa o no ocurra.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-19 en `main`, con archivo y línea.
- **Dicho por el desarrollador:** no comprobado por el agente.
- **Inferido:** sale de leer el código; se dice cómo se confirma.

## Qué hay hoy (verificado)

- **`duplicar_pedido`** (`views.py:508-532`): `@login_required` y `@require_POST` (04-01). Crea un `Pedido` copiando `cliente`, `resumen_pedido`, `detalles_pedido`, `valor_venta`, `fecha_entrega` e `imagen_referencia` (misma ruta, sin copiar el archivo). El estado queda en `PENDIENTE` y `creado_por` es quien duplica. Guarda, registra `pedido_duplicado` y redirige al detalle. **No copia los ítems ni los pagos y no usa `transaction.atomic()`** (hoy escribe una sola fila, así que la regla 8.3 no aplicaba).
- **`ItemPedido`** (`models.py:192-207`): `pedido` (`CASCADE`, `related_name='items'`), `producto` (`PROTECT`), `cantidad` (`DecimalField`, 2 decimales) y `precio_unitario` (`IntegerField`, «precio al momento de la venta»). `subtotal` es una propiedad.
- **`Producto`** (`models.py:109-`): `valor_neto`, `iva` y `valor_bruto` (calculados al guardar). **No tiene un campo de activo o inactivo** (verificado: no hay `activo` ni `is_active` en `models.py`). Por el `PROTECT`, un producto con ítems no se puede borrar.
- **`Pedido.fecha_entrega`** (`models.py:45`): admite nulo. `valor_venta` (`models.py:47`): entero, por defecto 0.
- **La regla del mínimo «mañana»** para la fecha de entrega **no está implementada en el código** (verificado: no aparece en `forms.py`, `views.py`, `pedido_form.html` ni `index.js`). La respuesta del cliente dice que el mínimo rige también al duplicar y al convertir (registro, sección 2), pero hoy no rige ni al crear.
- **Pruebas que fijan lo actual:** `test_pedidos.DuplicarPedidoTests` (`test_pedidos.py:328-382`). `test_lo_que_no_se_copia` afirma `self.assertFalse(nuevo.items.exists())` (`:374`), con un comentario `PENDIENTE_CLIENTE` ya respondido. El original de la prueba tiene un ítem de 2 × $5.000 y `valor_venta` de $25.000: los ítems y el total **no cuadran** a propósito, lo que importa para D3. También duplican `test_eventos_negocio.test_pedido_duplicado` (`:81-86`), `test_mutaciones_post` (`:51`, `:117`, `:139`) y `test_acceso`.

## Alcance

1. Al duplicar, copiar **cada ítem** del original (`producto`, `cantidad` y el precio que fije D1) al pedido nuevo.
2. **No copiar los pagos** (respuesta 2). El pedido nuevo nace con `estado_pago` `PENDIENTE`, como hoy.
3. **Una sola operación:** crear el pedido y sus ítems en un único `transaction.atomic()` (regla 8.3). El evento sigue con `on_commit`, así que si algo falla no queda pedido, ítems ni evento.
4. `valor_venta` y `fecha_entrega` según D3 y D4.
5. Consultas: leer los ítems del original con **una** consulta y crearlos con `bulk_create` (**una** consulta más). Se mide antes y después y se anota en la bitácora (regla 8.12). El aumento se reporta aunque sea en un POST.

## Fuera de alcance

- Copiar los pagos.
- Copiar el archivo de la imagen (sigue compartiendo la ruta, como hoy; AUD-02-023).
- Agregar un estado de activo o inactivo a `Producto`, cambiar el formulario de pedido o implementar el mínimo «mañana» al crear y al convertir cotizaciones (Épica 10, registro, sección 2).
- Duplicar cotizaciones.
- Formato de montos e ids (AUD-05-013, AUD-05-015).

## Decisiones abiertas (las resuelve el desarrollador)

| # | Decisión | Opciones | Recomendación |
| :- | :------- | :------- | :------------ |
| D1 | **Precio de cada ítem copiado** | **A.** El `precio_unitario` del ítem original (precio histórico). **B.** El precio actual del catálogo (`Producto.valor_neto` o `valor_bruto`). | **A.** Es la copia fiel que pidió el cliente («se copian los ítems») y no depende de la pregunta del IVA, que sigue abierta: con B habría que decidir si el precio es neto o bruto, y eso es una regla del negocio (`PENDIENTE_CLIENTE`). Quien reabre puede editar los precios después. |
| D2 | **Producto que ya no existe o ya no se ofrece** | **A.** Sin tratamiento especial: por el `PROTECT` el producto de un ítem no se puede borrar y `Producto` no tiene estado inactivo, así que el caso no ocurre hoy. Una prueba deja fijado que se copia el mismo producto. **B.** Agregar el concepto de producto inactivo y omitirlo o avisar. | **A.** El caso no existe en el esquema actual. B es funcionalidad nueva, con migración y RDA. Si algún día se agrega un estado inactivo, esa iteración decide qué pasa al duplicar. |
| D3 | **`valor_venta` del pedido nuevo** | **A.** Se conserva el del original, como hoy. **B.** Se recalcula como la suma de los subtotales copiados. | **A.** Hoy `valor_venta` no siempre es la suma de los ítems (descuentos, IVA u otros cargos; la prueba actual tiene 2 × $5.000 contra $25.000) y qué incluye un precio lo confirma el cliente (`AGENTS.md`, regla 7.2). Recalcular cambiaría el total que la persona espera. Con D1 A, en los pedidos que sí cuadran, A y B dan lo mismo. |
| D4 | **Fecha de entrega y el mínimo «mañana»** (respuesta del cliente: rige también al duplicar) | **A.** Copiar la fecha del original, como hoy (puede quedar en el pasado). **B.** Dejarla vacía (el campo admite nulo) para que la persona la defina al editar, con un mensaje en el detalle. **C.** Si la fecha original es anterior a mañana, poner mañana (`timezone.localdate() + 1 día`, regla 8.6); si no, copiarla. | **B.** Cumple la respuesta del cliente sin inventar una fecha: un duplicado con fecha pasada se vería atrasado en el panel, y C pone una fecha que nadie eligió. **Ojo:** el mínimo «mañana» no existe en el código al crear ni al convertir, así que aplicarlo solo al duplicar deja la regla a medias. Si el desarrollador prefiere no mezclarlo (RDA-007), elige A y la regla va completa a la Épica 10. |

## Pasos

0. Refrescar la réplica (`replica-local.md`): la revisión de la 04-10 borró dos pedidos y ya no es fiel. Respaldo de la réplica (`respaldo.md`).
1. Línea base: `python manage.py test pedidos` (tras la 04-10: 298 pruebas, `OK (expected failures=4)`) y consultas del POST de duplicar con un pedido de 3 ítems.
2. **Pruebas primero:** cambiar `test_lo_que_no_se_copia` (los ítems **sí** se copian y los pagos no) y escribir las nuevas de la tabla. Verlas fallar contra el código actual.
3. `duplicar_pedido`: `transaction.atomic()` con el pedido y `ItemPedido.objects.bulk_create(...)`, según D1 a D4. Evento con `on_commit`, como hoy.
4. `check` y `makemigrations --check --dry-run` sin cambios.
5. Revisión manual en la réplica, en escritorio y a 360 px: reabrir un pedido con varios ítems (detalle con los mismos productos, cantidades y precios; sin pagos; total y fecha según D3 y D4) y uno sin ítems.
6. Bitácora, registro y estado «En revisión».

## Pruebas

| Punto | Prueba |
| :---- | :----- |
| Ítems copiados | Original con 2 ítems (uno con cantidad decimal, `Decimal('1.5')`): el nuevo tiene 2 ítems con el mismo producto, la misma cantidad y el precio de D1; el original conserva los suyos (no se mueven). |
| Pagos no copiados | El original con un pago: el nuevo no tiene pagos y su `estado_pago` es `PENDIENTE`. |
| Sin ítems | Duplicar un pedido sin ítems funciona como hoy (0 ítems, sin error). |
| `valor_venta` (D3) | Con ítems que no cuadran con el total, el nuevo tiene el valor que fije D3. |
| Fecha (D4) | Con fecha original pasada y con fecha futura (hora congelada con `ayudas.congelar_hora`), el nuevo tiene la fecha que fije D4. |
| Atomicidad | Con `bulk_create` forzado a fallar (`mock`): no queda pedido nuevo, ni ítems, ni evento. |
| Evento | Un solo `pedido_duplicado` con los identificadores, como hoy (`test_eventos_negocio`). |
| Solo POST | GET sigue en 405 (`test_mutaciones_post`); sin sesión, va al acceso; un id inexistente da 404 (`test_acceso`). |
| Precio con D1 B (si se elige) | Cambiar el precio del producto después del pedido original: el ítem copiado toma el precio actual. |
| Consultas | Antes y después del POST, anotados en la bitácora. |

**Deben fallar antes del arreglo:** ítems copiados, el `test_lo_que_no_se_copia` modificado, la atomicidad con `bulk_create` y, según D4, la de la fecha.

## Despliegue (lo hace el desarrollador)

1. Respaldo de rutina, descargado y verificado (`respaldo.md`).
2. `git diff --stat v4.2-confirmar-eliminar-pedido -- requirements.txt pedidos/migrations PedidosApp/settings.py pedidos/static` sin salida: sin `pip`, `migrate` ni `collectstatic`.
3. Commit, etiqueta anotada `v14.2-duplicar-items` (propuesta), `git fetch --tags`, `git checkout` de la etiqueta en PythonAnywhere, `git describe` y Reload.
4. Día 0: reabrir un **pedido de prueba** con ítems, comprobar el detalle del nuevo (ítems, sin pagos, total y fecha) y después borrar los dos pedidos de prueba. `server.log` y `error.log` sin errores nuevos.

## Plan de retroceso

- `retroceso.md`, caso 1 (sin migraciones): volver a `v4.2-confirmar-eliminar-pedido` y Reload.
- Los pedidos duplicados con ítems mientras tanto quedan así y son datos válidos. No hay nada que deshacer.

## Criterio de término

- Tabla de pruebas en verde y resto de la suite sin cambios en los fallos esperados.
- Revisión manual en la réplica refrescada, en escritorio y a 360 px.
- Sin migración nueva y consultas anotadas.
- Día 0 en producción hecho, y AUD-05-012 resuelto y verificado.

## Riesgos

- **Total y detalle que no cuadran:** con D3 A, un pedido cuyo total no era la suma de los ítems sigue igual en la copia. No es nuevo, pero ahora el detalle está a la vista.
- **Precios viejos:** con D1 A, si el catálogo subió, el pedido reabierto lleva el precio antiguo hasta que alguien lo edite.
- **Regla de la fecha a medias (D4 B o C):** el mínimo «mañana» rige al duplicar, pero todavía no al crear ni al convertir.
- **Una o dos consultas más en el POST de duplicar:** se miden. Es un POST que se usa poco y el aumento no depende del número de ítems (`bulk_create`).
- **Un despliegue, un propósito (RDA-007):** va solo, sin la regla de la fecha completa ni el formato de montos.
