# Iteración 03-03 · Fronteras transaccionales por vista

- **Épica:** 03 · Integridad transaccional
- **Estado:** En revisión (2026-11-04). Ejecutada en local con las ocho decisiones del desarrollador del 2026-11-04 (todas la opción A) ([bitacora-03-03](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-03.md)); falta su revisión manual. Sin despliegue propio: viaja con la 03-05. Historial de estados: Pendiente (redactada el 2026-11-04, [bitacora-03-03-redaccion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-03-redaccion.md)) → En revisión (2026-11-04).
- **Subfase del plan:** 3.3 «Revisión de fronteras transaccionales» (`plan-de-trabajo.md:344`)
- **Depende de:** 03-02 (Terminada el 2026-11-04)
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-013 (errores con `logging` en `server.log`, sin identificador de correlación), RDA-015 (las transacciones pasarán a los servicios en la 07-02), RDA-019 (atomicidad con `transaction.atomic` explícito y la captura **fuera** del bloque).
- **Hallazgos que cierra:** AUD-01-001 y AUD-01-002 (decisión del desarrollador del 2026-11-04: se cierran aquí, con R1, R2 y R4), AUD-02-004 (R10, R11 y R12) y AUD-02-005 (R13).
- **Hallazgos relacionados:** AUD-02-008 (R3 ya pasó a verde en la 03-02; su estado lo decide el desarrollador), AUD-02-014 (**no se cierra**: depende del cliente), AUD-02-027 (R18; la cierra esta iteración: la decisión 3-A **reemplaza** la del 2026-10-27 que la dejaba en la 03-04) y AUD-02-028 (R19; la corrige la 04-01, decisión 5-A).
- **Cambio de esquema:** Ninguno.
- **Respaldo previo al despliegue:** No lo exige por sí misma (sin migraciones). Lo decide el desarrollador al planificar la 03-05; la decisión 6-A (no reparar datos) no agrega escrituras masivas.
- **Etiqueta y ventana:** sin despliegue propio; viaja con la 03-05, igual que la 03-01 y la 03-02.

## Objetivo

Que cada vista que escribe más de una fila relacionada lo haga dentro de **un único** `transaction.atomic()`, con la excepción saliendo del bloque (RDA-019): si algo falla, no queda nada a medias en la base. Es la parte de la épica que cierra la pérdida de ítems al editar, el `estado_pago` desincronizado y la doble conversión de una cotización.

## Cómo se lee este documento

- **Documentado:** está escrito en el repositorio o en la planificación; se cita archivo y línea (leídos el 2026-11-04).
- **Inferido:** sale de leer el código, no de ejecutarlo ni medirlo. Se marca «(inferido)». Las predicciones de pruebas (cuántos fallos esperados quedan) se **confirman al ejecutar**.

## Alcance contra la definición de la épica

Verificado contra `definicion-epica-03.md` (alcance 1 a 3) y `plan-de-trabajo.md:344-358`.

| Pieza | Fuente | En esta iteración |
| :---- | :----- | :---------------- |
| Atomicidad de creación y edición de pedidos y cotizaciones | Alcance 3 de la épica; plan 3.3 | Sí |
| Conversión de cotización a pedido | Alcance 3; plan 3.3 | Sí |
| Registro, edición y eliminación de pagos | Alcance 3; plan 3.3 | Sí |
| `estado_pago` dentro de la misma transacción, incluido el pedido anterior si un pago cambia de pedido (AUD-02-004) | Alcance 3, primer punto | Sí |
| Rechazar una cotización ya aceptada y validar fecha y abono con un formulario (AUD-02-005) | Alcance 3, segundo punto | Sí: decisión 3-A (fecha, abono y estado) |
| Las 3 capturas de ítems que siguen (`editar_pedido`, `crear_cotizacion`, `editar_cotizacion`) | Alcance 2; `iteracion-03-02`, «Fuera de alcance» | Sí |
| Imágenes de referencia huérfanas | «Decisiones de la épica» (`definicion-epica-03.md:47`); plan 3.3 «Consideración adicional» | Sí: decisión 2-A (aceptar y documentar) |
| Cierre de AUD-01-001 y AUD-01-002 | Registro, decisión del 2026-11-04 | Sí |
| Mensajes al usuario, conservación del formulario y envío único (R21) | Alcance 4 y 6 | **No: 03-04** |
| Hallazgos de otras épicas (POST, respaldo, `float`, servicios) | — | **No** (ver «Fuera de alcance») |

## Qué hace hoy (evidencia leída el 2026-11-04)

### Las vistas de escritura y su frontera

| Vista | Lugar en `views.py` | `atomic` | Captura | Qué queda si falla a mitad |
| :---- | :------------------ | :------: | :------ | :------------------------- |
| `crear_pedido` | `:156-239` | Sí (`:166`) | Ninguna desde la 03-02 | Nada: se revierte (R3, ya verde). El pago se crea en `:199-211` pero **no** recalcula `estado_pago` |
| `editar_pedido` | `:241-292` | No | `except Exception` en `:264` | `form.save()` (`:249`) ya escribió; los ítems se borran (`:254`) y se recrean hasta el fallo. Redirige como si hubiera salido bien |
| `crear_cotizacion` | `:729-772` | No | `:756` | La cotización (`:739`) queda con ítems parciales |
| `editar_cotizacion` | `:774-826` | No | `:800` | Igual que `editar_pedido`, en cotizaciones. Rechaza las `ACEPTADA` antes (`:779-780`) |
| `convertir_a_pedido` | `:841-915` | No | `except ValueError` en `:855` (abono) | Crea el pedido (`:860`), copia ítems (`:871`), crea el pago (`:883`) y cierra la cotización (`:902`) en escrituras separadas |
| `ingresar_pago` | `:1361-1425` | No | Ninguna | Guarda el pago (`:1384`) y recalcula `estado_pago` con lógica propia en línea (`:1402-1413`) |
| `editar_pago` | `:1427-1455` | No | Ninguna | Guarda (`:1439`) y recalcula solo el pedido **nuevo** (`:1442`) |
| `eliminar_pago` | `:1457-1478` | No | Ninguna | Borra (`:1468`) y recalcula (`:1471`) en escrituras separadas |

- **Línea del abono:** la 03-02 citaba `views.py:858` para el `except ValueError`. Tras retirar la captura de `crear_pedido`, la línea vigente es **`:855`** (verificado). Las demás líneas que cita la 03-02 (`:191`, `:267`, `:759`, `:803`) también se desplazaron: los números de arriba son los vigentes.
- **Comentarios «se corrige en 03-02»:** `views.py:265`, `:757` y `:801`. Desaparecen junto con las tres capturas. El comentario de `:180` es de la 03-02 y queda.
- **Eventos:** `registrar_evento` escribe con `transaction.on_commit` (`eventos.py`). Dentro de un `atomic` revertido no deja rastro; hoy, en `editar_pedido`, el evento `pedido_modificado` (`:268`) se registra aunque los ítems se hayan perdido (`iteracion-03-02`, «Efectos laterales»).

### `estado_pago`

- **El ayudante existe:** `actualizar_estado_pago_pedido` (`views.py:142-150`) calcula `PAGADO` si el saldo es ≤ 0, `PARCIAL` si hay pagos y `PENDIENTE` si no. Lo usan `editar_pago` y `eliminar_pago`. `ingresar_pago` repite la misma lógica en línea (`:1402-1413`, equivalente) y `convertir_a_pedido` la repite en dos ramas (`:893-896`).
- **Dónde falta (R10 a R12):** `crear_pedido` con abono lo deja `PENDIENTE` (`:174` fija el estado y `:199-211` crea el pago sin recalcular); `editar_pedido` no lo recalcula si cambia `valor_venta`; `editar_pago` no recalcula el pedido anterior si el pago cambia de pedido (`pedido_asociado` se lee en `:1434` y no se vuelve a usar).
- **Medido en producción (2026-10-20, AUD-02-004):** 610 de 870 pedidos con `estado_pago` desincronizado.
- **Quién lo lee (inferido, por búsqueda):** `estado_pago` aparece solo en `models.py`, `forms.py` (excluido del formulario), `views.py` y migraciones. **No hay ninguna coincidencia en las plantillas** y el admin no lo usa. Hoy ninguna pantalla lo muestra: el saldo y el porcentaje que se ven salen de las propiedades `saldo_pendiente` y `porcentaje_pagado` (`models.py:65-81`), que calculan desde los pagos. Corregir el código no cambia lo que el usuario ve hoy; sí deja el dato correcto para quien lo lea después.
- **Regla provisoria:** el oráculo de las pruebas (`ayudas.estado_pago_esperado`) cuenta un pedido de valor $0 como `PAGADO`. Esa regla es `PENDIENTE_CLIENTE` (fila de `registro-pendientes.md`, sección 2). Producción no tenía pedidos de $0 al 2026-10-20.

### La conversión (`convertir_a_pedido`)

- **No mira el estado:** ni el GET ni el POST comprueban que la cotización siga sin convertir. La pantalla de detalle solo oculta el botón y muestra la etiqueta «ACEPTADA» (`cotizacion_detail.html:46-48`, `:99`, `:109`): un doble clic o un reenvío del POST crea otro pedido (R13).
- **Sin formulario:** `fecha_entrega` y `valor_abonado` se leen de `request.POST` (`:851-852`). El abono no numérico pasa a 0 sin aviso (`:853-856`). La plantilla es de campos escritos a mano, sin errores de formulario (`cotizacion_convertir.html:50`, `:67`). Una fecha vacía lanza una excepción al guardar y responde 500 (R18, AUD-02-027, asignado hoy a la 03-04).
- **Reglas hoy fijadas por pruebas de caracterización** (`test_cotizaciones.py:140-174`, `pruebas.md` sección 9): abono no numérico y abono negativo **no crean pago** y el pedido queda `PENDIENTE`; el valor de venta del pedido es `valor_total` de la cotización **sin IVA** (`PENDIENTE_CLIENTE`, AUD-02-014).
- **Regla análoga ya existente:** `PedidoForm.clean_abono_inicial` (`forms.py:49-56`) rechaza un abono mayor que el total, solo cuando el total es mayor que 0.

### Lo que la pantalla no hace por el usuario (relevante para la 03-04)

- **Los mensajes de Django casi no se ven (inferido, por búsqueda).** La palabra `message` aparece en una sola plantilla, `restaurar_bd.html:100-118`. Ni `base.html` ni las demás recorren `messages`, aunque el procesador de contexto está activo (`settings.py`) y `views.py` tiene 10 llamadas a `messages.*`. Consecuencias: un `messages.error` hacia otra pantalla no se verá. Esto incluye el aviso de `generar_respaldo_bd` (`views.py:1118`, redirige a `respaldar_bd`, que no recorre los mensajes). No se corrige aquí; condiciona las decisiones 1 y 4 y a la 03-04.

### Pruebas que esta iteración toca

| Prueba | Lugar | Hoy | Qué cambia |
| :----- | :---- | :-- | :--------- |
| R1, R2, R4 | `test_regresiones.py:122-176` | Fallo esperado por la aserción de los datos | Ajustar como R3 (`raise_request_exception = False`, `absorber_errores` con `pedidos` y `django.request`); luego pasan a verde |
| R10, R11, R12 | `:298-335` | Fallo esperado | Pasan a verde |
| R13 | `:348-356` | Fallo esperado | Pasa a verde |
| R18 | `:358-368` | Fallo esperado, asignado a la 03-04 | Pasa a verde **si** la decisión 3 es A |
| R19 | `:405-414` | Fallo esperado, sin iteración | Solo si la decisión 5 es B |
| `CapturasItemsTests` (3) | `test_capturas_amplias.py:42-75` | Afirman «redirección y un `ERROR` de `pedidos.views`» | Dejan de ser ciertas: se reescriben o se retiran, porque las vistas pasarán a responder 500 |
| `test_abono` | `test_cotizaciones.py:140-174` | Fija «no numérico» y «negativo» como abono 0 | Cambia con la decisión 3 (A y B) |

**Trampa conocida (03-02):** una excepción que sale de la vista sale también por el cliente de pruebas salvo `raise_request_exception = False`. R1, R2 y R4 deben ajustarse **antes** de corregir; si no, seguirían como fallo esperado por el error y no por los datos (`pruebas.md`, sección 7.1).

## Decisiones

Resueltas el 2026-11-04: el desarrollador eligió la opción A, la recomendada, en las ocho. Las opciones se conservan como constancia de lo que se evaluó.

### Decisión 1 · Qué ve el usuario cuando falla un ítem, hasta la 03-04 (elegida: A)

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Propagar la excepción (recomendada)** | Las tres vistas quedan como `crear_pedido` desde la 03-02: el error sale del `atomic`, se revierte todo y Django responde la página 500 con una línea `django.request` con traza | Mismo patrón que la 03-02 y que RDA-019. Cumple la regla 4 sin captura amplia. Una sola forma de fallar en las cuatro vistas de ítems. Todo viaja con la 03-04 | El usuario ve la página 500 y pierde lo que escribió hasta la 03-04; como las dos viajan con la 03-05, no llega a producción separada |
| **B. Capturar excepciones concretas fuera del `atomic` y avisar** | `try: with transaction.atomic(): … except (json.JSONDecodeError, KeyError, TypeError, ValueError, Producto.DoesNotExist):` con `logger.exception` y `messages.error` | El usuario se entera sin ver un 500 | **El aviso no se vería**: los mensajes no se muestran fuera de `restaurar_bd.html` (ver arriba). Adelanta el contrato de la 03-04 y fija una lista de excepciones. Es la opción D de la 03-02, que el desarrollador no eligió |

### Decisión 2 · Imágenes de referencia huérfanas (elegida: A)

`PedidoForm` escribe el archivo en `media/referencias/` cuando se guarda el pedido (`models.py:42`; en `crear_pedido`, `pedido.save()` en `:176`; en `editar_pedido`, `form.save()` en `:249`). El sistema de archivos no participa en la transacción: si esta se revierte, el archivo queda en disco (plan 3.3, «Consideración adicional»). Disco escaso y `media/` sin copia (AUD-02-023).

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Aceptar y documentar (recomendada)** | No se toca el archivo. Se anota en `despliegue.md` o en la bitácora que un fallo con imagen puede dejar un archivo sin pedido | Cambio mínimo. Sin riesgo de borrar un archivo vivo. Solo ocurre si falla un ítem **y** el formulario traía imagen (inferido: raro, sin fallos de ítems medidos en producción) | Un archivo huérfano por evento, sin límite de tamaño más allá del que tenga la imagen |
| **B. Borrar el archivo recién escrito si el bloque falla, y relanzar** | `try/except` alrededor del `atomic` que borra el archivo y hace `raise` | Cumple «no deja rastro» también en disco | **Puede borrar un archivo vivo**: en `editar_pedido` sin imagen nueva, `imagen_referencia` apunta al archivo anterior; en `duplicar_pedido` el duplicado comparte la ruta del original (`views.py:410`). Un error aquí destruye datos que no tienen copia |
| **C. Escribir el archivo después de confirmar** | Mover la escritura a `transaction.on_commit` | Nunca queda huérfano por un fallo de la base | Cambia cómo se guarda la imagen en el formulario; el más grande y el que más prueba exige |

### Decisión 3 · Qué valida el formulario de la conversión (elegida: A)

La épica pide validar **fecha y abono** con un formulario (`definicion-epica-03.md`, alcance 3). Pero R18 (fecha vacía, AUD-02-027) está asignada a la 03-04 (decisión del desarrollador, 2026-10-27, `pruebas.md` fila R18). Un formulario de Django exige la fecha por defecto, así que lo que se haga con la fecha decide dónde cae R18.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Fecha, abono y estado (recomendada)** | Formulario nuevo con `fecha_entrega` requerida y `valor_abonado` entero ≥ 0, y el abono no mayor que `valor_total` cuando este es > 0 (misma regla que `PedidoForm`, `forms.py:49-56`). Un error devuelve la página de conversión con los campos y el error | Cumple lo que dice la épica y AUD-02-005. Cierra AUD-02-027 de paso: R18 pasa a verde aquí (fallos esperados finales: 9). Sin formulario a medias | **Contradice la asignación de AUD-02-027 y R18 a la 03-04.** Cambia lo que fijan las pruebas de caracterización de «no numérico» y «negativo» (hoy abono 0). Necesita mostrar errores en `cotizacion_convertir.html`, que hoy son campos escritos a mano (cambio de plantilla: leer `DESIGN.md`, revisión a 360 px). La regla de $0 y de sobrepago es `PENDIENTE_CLIENTE` y queda como la del pedido |
| **B. Solo abono y estado; la fecha sigue sin validar** | El formulario valida el abono; `fecha_entrega` se sigue leyendo de `request.POST` | R18 sigue en la 03-04 como decidió el desarrollador | Formulario que ignora a propósito un campo que la misma pantalla exige; la fecha vacía sigue dando 500 hasta la 03-04 (viajan juntas a producción). El `atomic` revertiría todo, pero igual hay 500 |
| **C. Sin formulario: validar a mano en la vista** | `try/except ValueError` ampliado y comprobaciones sueltas | Menos código nuevo | Incumple lo que pide la épica y repite lo que Django ya resuelve; deja la vista más larga justo antes de que la 07-02 la mueva a un servicio |

### Decisión 4 · Qué ve el usuario ante una conversión repetida (elegida: A)

El rechazo ocurre en el servidor, dentro del `atomic` y al **inicio** de la vista (GET y POST), como ya hace `editar_cotizacion` (`views.py:779-780`).

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Redirigir al detalle de la cotización (recomendada)** | Sin mensaje: el detalle ya muestra la etiqueta «ACEPTADA» y no ofrece «Convertir» | Funciona hoy sin tocar plantillas ni depender de `messages`. Mismo patrón que `editar_cotizacion` | No explica por qué volvió. El pedido ya creado no se enlaza desde la cotización (no hay clave entre ambos; la relación solo queda en el texto del evento, `views.py:904-905`) |
| **B. Redirigir con `messages.warning`** | Igual que A, con un aviso | Explica | **No se vería** (los mensajes no se muestran en el detalle). Sería texto sin efecto hasta que la 03-04 resuelva dónde se muestran |
| **C. Responder un error HTTP (409)** | Página de error | Semántica clara | Es un error para un doble clic corriente; mostraría la página 500/404 de la aplicación o una nueva |

### Decisión 5 · Quién corrige AUD-02-028 (R19, `duplicar_pedido` sin `creado_por`) (elegida: A)

`duplicar_pedido` crea el pedido sin `creado_por` (`views.py:403-411`). Es una sola escritura: no necesita frontera transaccional. `auditoria-tecnica.md` (fila AUD-02-028) deja la iteración `PENDIENTE_DESARROLLADOR` con candidatas 04-01 y 03-03.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. 04-01 (recomendada)** | La 04-01 reescribe `duplicar_pedido` para aceptar solo POST (AUD-02-006, R6b); `creado_por = request.user` entra en la misma edición | Un despliegue, un propósito (RDA-007): no mezcla autoría con integridad. Una sola reescritura de la vista | R19 queda abierto hasta la 04-01, después de la Épica 03 |
| **B. 03-03** | Se agrega la línea y R19 pasa a verde aquí (fallos esperados finales: uno menos) | Cierra un hallazgo pequeño antes | No es transaccional: mezcla propósitos. La 04-01 vuelve a editar la misma vista |
| **C. Dejar sin asignar** | Sin cambios | Nada que hacer ahora | El hallazgo sigue flotando |

### Decisión 6 · Los `estado_pago` históricos desincronizados (elegida: A)

La corrección del código evita nuevas desincronizaciones; **no** repara las filas existentes (610 de 870 en la medición del 2026-10-20). Inferido: como ninguna pantalla lee `estado_pago`, no hay efecto visible hoy.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. No reparar ahora (recomendada)** | Se deja registrado, con la cifra, como pendiente para la primera iteración que lea el campo | Sin escrituras masivas en producción. No fija reglas que el cliente no confirmó ($0 y sobrepago) | El dato sigue incorrecto en 7 de cada 10 pedidos; cualquier lector futuro lo hereda. «Resuelto» para AUD-02-004 significa «código corregido», no «datos reparados» |
| **B. Orden de gestión de un solo uso** | Un comando idempotente, con `--dry-run`, que recalcula desde los pagos; lo ejecuta el desarrollador en la réplica y luego en producción | Deja el dato coherente. Reversible con el respaldo previo | Escribe en producción (respaldo previo obligatorio y ensayo en la réplica). Aplica la regla provisoria de $0 y de sobrepago. Código que se usa una vez |
| **C. Migración de datos (`RunPython`)** | Igual, dentro de una migración | Se ejecuta sola en el despliegue | Una migración que modifica datos no encaja en las clases 1 a 3 de `AGENTS.md`, sección 8, y exige consulta previa para crearla. No se puede ensayar a voluntad |

### Decisión 7 · Cuántas iteraciones (elegida: A)

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Una sola, con pasos ordenados (recomendada)** | Esta iteración, con un bloque de verificación por paso | Un solo propósito (integridad transaccional); sin despliegue propio. Los siete pasos son independientes entre sí salvo el orden indicado | Es la más grande de la épica: 8 vistas y entre 7 y 9 regresiones |
| **B. Dividir en dos** | Ítems (R1, R2, R4) y pagos más conversión (R10 a R13) | Revisiones más chicas | Obliga a un número nuevo (el siguiente correlativo libre de la épica, 03-06) y a cambiar el orden y la tabla de la épica; ambas viajan juntas igual con la 03-05 |

### Decisión 8 · El abono inicial que la edición descarta (elegida: A)

AUD-02-004 también dice que el formulario de edición muestra el campo de abono inicial y descarta en silencio lo que se ingrese (`editar_pedido` no crea pagos). La definición de la épica, en cambio, solo pide recalcular `estado_pago`. No tiene regresión asignada.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Fuera de alcance; anotarlo como propuesta (recomendada)** | Queda en `registro-pendientes.md`, sección 4, para una iteración de interfaz | Mantiene la 03-03 en lo transaccional | El comportamiento engañoso sigue |
| **B. Ocultar el campo al editar** | Cambio de plantilla y de formulario | Quita el engaño | Es interfaz, no transacción: obliga a leer `DESIGN.md`, probar a 360 px y mezcla propósitos |

## Tareas (en este orden, una vez tomadas las decisiones)

Todo con `DB_NAME=manzagrafica_replica` y el MySQL local de Docker encendido. Cada paso empieza por la prueba (regla 15 de `AGENTS.md`) y termina con las pruebas del dominio en verde. El orden va de lo más parecido a la 03-02 a lo más grande, y deja la conversión al final porque depende del ayudante de `estado_pago` y de las decisiones 3 y 4.

0. **Línea de partida:** `python manage.py test pedidos` → 189 pruebas, `OK (expected failures=17)`. Registrar el número de consultas de las vistas que se tocan (regla 12), por si cambia.
1. **Ajustar R1, R2 y R4** (`raise_request_exception = False` y `absorber_errores` con `pedidos` y `django.request`) y comprobar que **siguen fallando por la aserción de los datos**, no por el error. Escribir las pruebas nuevas de `editar_pedido`, `crear_cotizacion` y `editar_cotizacion` con el modelo de `CrearPedidoItemFallidoTests`: cinco causas de fallo de ítem; no queda rastro (ítems y valor anteriores intactos en las ediciones); respuesta 500 con la plantilla de la 01-03; una sola línea `django.request`; ni `except Exception` en la vista; ningún evento. Reescribir o retirar las 3 pruebas de `CapturasItemsTests`.
2. **Cotizaciones (R4 y R2):** `transaction.atomic()` alrededor de `form.save()` y los ítems, sin captura; en la edición, el borrado de ítems va dentro. Quitar los comentarios «se corrige en 03-02».
3. **`editar_pedido` (R1 y R11):** el mismo bloque, más `actualizar_estado_pago_pedido` dentro del `atomic` después del cambio de ítems y de `valor_venta` (siempre, no solo si cambió el valor: es idempotente). El evento `pedido_modificado` va dentro; se escribe al confirmar.
4. **`crear_pedido` (R10):** dentro del `atomic` que ya existe, recalcular `estado_pago` después de crear el pago inicial (solo cuando hay abono, para no cambiar el estado de un pedido sin pagos).
5. **Pagos (R12):** `ingresar_pago`, `editar_pago` y `eliminar_pago` con `atomic` propio.
   - `ingresar_pago`: reemplaza la lógica en línea por `actualizar_estado_pago_pedido` (mismo resultado, una sola fuente).
   - `editar_pago`: guarda el pedido anterior **antes** de `form.save()` y, si cambió, recalcula **los dos** dentro del bloque.
   - `eliminar_pago`: borrar y recalcular dentro del bloque. La plantilla de confirmación y el GET son de la 04-01 (R7).
6. **Conversión (R13, y R18 si la decisión 3 es A):** `atomic` que abarca la lectura de la cotización con bloqueo de fila (`select_for_update`; inferido: con un solo worker las peticiones son en serie y la comprobación de estado bastaría, pero el bloqueo no cuesta y no depende de esa configuración), el rechazo si está `ACEPTADA` (decisión 4), el formulario (decisión 3), el pedido, los ítems, el pago, `estado_pago` y el cierre de la cotización. Conservar `valor_venta = cotizacion.valor_total` sin cambios (AUD-02-014).
7. **Cierre técnico:** quitar `@expectedFailure` y `@tag('regresion')` de las regresiones que pasan a verde y actualizar `docs/operacion/pruebas.md` (valor vigente, filas retiradas y viñeta). Actualizar las pruebas de caracterización que la decisión 3 cambia. Comprobar que `despliegue.md`, paso 1, sigue remitiendo a `pruebas.md` para el número.
8. **Verificación:** `python manage.py test pedidos` en tres ejecuciones, `check`, `makemigrations --check --dry-run` y revisión manual (más abajo).
9. **Cierre documental:** bitácora, registro, y las notas fechadas de AUD-01-001, AUD-01-002, AUD-02-004, AUD-02-005 (y las que correspondan por las decisiones 3 y 5). Aplicar «Resuelto en 03-03» solo si las pruebas verdes lo respaldan.

## Regresiones que pasan a verde (predicción por lectura)

| Regresión | Hallazgo | Paso | Pasa a verde |
| :-------- | :------- | :--: | :----------- |
| R1 | AUD-01-002 | 3 | Siempre |
| R2 | AUD-01-002 | 2 | Siempre |
| R4 | AUD-01-002 | 2 | Siempre |
| R10 | AUD-02-004 | 4 | Siempre |
| R11 | AUD-02-004 | 3 | Siempre |
| R12 | AUD-02-004 | 5 | Siempre |
| R13 | AUD-02-005 | 6 | Siempre |
| R18 | AUD-02-027 | 6 | Sí (decisión 3-A) |
| R19 | AUD-02-028 | — | No: la corrige la 04-01 (decisión 5-A) |

Con las decisiones tomadas (3-A y 5-A) pasan a verde ocho regresiones y los fallos esperados bajan de 17 a **9** (predicción de la redacción: 9). Quedan R6a, R6b, R6c, R7, R8, R9, R14, R15 y R19 (04-01, 04-06, 06-01 y 07-02). **Medido:** `OK (expected failures=9)`, ver el resultado más abajo.

## Criterios de aceptación

- [x] Las decisiones 1 a 8 están registradas antes de implementar (todas A, 2026-11-04; sección «Decisiones del desarrollador»).
- [x] Las pruebas se escribieron antes de la corrección y fallaban por la razón correcta: R1 y R2 por los ítems que quedaban (`[(2, 3.00, 4000)] != [(1, 1.00, 10000)]`), R4 por `(1, 1) != (0, 0)`; R10 a R12 por `estado_pago` (`'PENDIENTE' != 'PARCIAL'`, `'PAGADO' != 'PARCIAL'`, `'PAGADO' != 'PENDIENTE'`); R13 por `2 != 1`. Detalle en la bitácora.
- [x] `editar_pedido`, `crear_cotizacion`, `editar_cotizacion`, `convertir_a_pedido`, `ingresar_pago`, `editar_pago` y `eliminar_pago` escriben dentro de **un** `transaction.atomic()` y la excepción sale del bloque; ninguna contiene `except Exception` (pruebas `test_la_vista_no_captura_y_abre_su_transaccion` y `test_las_vistas_de_pagos_abren_su_transaccion_y_no_capturan`).
- [x] Un ítem fallido en cada una de las tres vistas de ítems no deja pedido ni cotización a medias, deja los ítems y el valor anteriores en las ediciones, no escribe evento, responde 500 con `pedidos/errors/500.html` y deja **una** línea `django.request` con traza (decisión 1-A; cinco causas por vista).
- [x] R1, R2, R4, R10, R11, R12, R13 y R18 en verde y sin marcas; R19 sigue como fallo esperado hasta la 04-01 (decisión 5-A).
- [x] Convertir dos veces la misma cotización crea un solo pedido, por el POST y por la URL directa (GET), y el segundo intento termina en el detalle de la cotización, sin mensaje (`ConversionRepetidaTests`, decisión 4-A).
- [x] La fecha y el abono de la conversión se validan con un formulario y el abono ya no pasa a 0 sin aviso (decisión 3-A, `ConversionFormularioTests`); `valor_venta` sigue siendo `valor_total` sin IVA.
- [x] Un pago que cambia de pedido deja ambos pedidos con el `estado_pago` que da el oráculo (R12).
- [x] `pruebas.md` y la bitácora dicen `expected failures=9`; `python manage.py test pedidos` → 220 pruebas, `OK (expected failures=9)` en tres ejecuciones; `check` limpio; `makemigrations --check --dry-run`: `No changes detected` (detalle en la bitácora).
- [x] AUD-01-001, AUD-01-002, AUD-02-004 y AUD-02-005 anotados como resueltos en la 03-03 (código, con despliegue en la 03-05), con la evidencia de las pruebas. Por decisión del desarrollador, también AUD-02-008, y AUD-02-027 por la decisión 3-A.
- [ ] Revisión manual hecha (más abajo).
- [x] Los `PENDIENTE_CLIENTE` de AUD-02-014 y del valor $0/sobrepago siguen abiertos y sin cambios de comportamiento (`test_valor_venta_es_el_valor_total_sin_iva` y `test_con_total_cero_cualquier_abono_se_acepta`).

## Revisión manual (la hace el desarrollador, contra la réplica local)

Con `DEBUG=False` y `runserver --insecure`, en escritorio y a 360 px:

1. **Editar un pedido con un ítem fallido** (alterar `items_json` a un `producto_id` inexistente): página 500 de la aplicación; al abrir el detalle, los ítems y el `valor_venta` anteriores siguen igual.
2. **Crear y editar una cotización con un ítem fallido:** página 500; sin cotización nueva o con la anterior intacta.
3. **Convertir una cotización dos veces** (segundo intento desde la URL directa o con el botón «atrás»): un solo pedido; el segundo intento termina en el detalle de la cotización (decisión 4).
4. **Convertir con un abono inválido** (decisión 3-A): la página de conversión vuelve con el error visible y sin perder lo escrito, en ambos anchos.
5. **Mover un pago de pedido:** el saldo y el porcentaje de ambos pedidos cambian como corresponde. `estado_pago` **no** se ve en ninguna pantalla (inferido, por búsqueda): se verifica con las pruebas y, si quieres, con una consulta de solo lectura en la réplica.
6. Los pedidos y cotizaciones de prueba quedan en la réplica y se limpian al refrescarla al cierre de la Épica 03 (AUD-05-002).

Instrucciones de lo que no puede hacer el agente (consultas a la réplica) se entregarán con la ejecución, no antes. No hay evidencia que pedir a producción.

## Resultado de la ejecución (2026-11-04)

Detalle y mediciones en [bitacora-03-03](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-03.md).

- **Pasos 0 a 8** ejecutados en orden y con la prueba primero. Línea de partida: 189 pruebas, `OK (expected failures=17)`.
- **Qué cambió en el código:** `views.py` (siete vistas con `transaction.atomic()`, `convertir_a_pedido` con `select_for_update`, ayudante de `estado_pago` que guarda solo ese campo), `forms.py` (`ConversionCotizacionForm`) y `cotizacion_convertir.html` (errores junto a cada campo, valores conservados y método de pago elegido).
- **Pruebas:** archivo nuevo `test_fronteras_transaccionales.py`; R1, R2, R4, R10 a R13 y R18 sin marcas; se retiraron las tres pruebas de `CapturasItemsTests` (las reemplazan las nuevas) y se sacaron de `test_abono` los dos abonos inválidos, que ahora se rechazan.
- **Sin** `messages.*` nuevos, **sin** migraciones, sin validar ni recalcular el precio del ítem.

## Fuera de alcance

- Mensajes al usuario, dónde se muestran, conservación del formulario y envío único (R21): 03-04. Hasta entonces, un ítem fallido muestra la página 500 y el formulario se pierde.
- Validar el precio del ítem contra el catálogo o recalcularlo en el servidor: **prohibido** (regla de negocio confirmada el 2026-10-27, `pruebas.md` sección 9).
- Hacer que los mutadores acepten solo POST (cambiar estado, duplicar, respaldo), la plantilla de eliminar pago (R7) y `duplicar_pedido`, incluido `creado_por` (R19, decisión 5-A): 04-01.
- Respaldo y restauración, la excepción propia de `utils.py` y el `.sql` vacío: 04-04.
- Borrado en cascada del historial (R14): 04-06.
- `float(item['cantidad'])` en lugar de `Decimal` y el porcentaje pagado con `float` (R15): 07-02. Mover las transacciones a servicios: 07-02 (RDA-015).
- Fechas en UTC (R8, R9): 06-01.
- Corregir el valor de venta de la conversión (neto o con IVA, AUD-02-014): depende de la respuesta del cliente.
- Los 13 errores de plantilla de AUD-02-021 (R16 reservado): sin causa conocida.
- Que `generar_respaldo_bd` y otros avisos no se vean por no recorrer `messages`: 03-04, con la decisión de la épica sobre dónde mostrar errores. Se anota en el registro como observación.

## Despliegue

- Cambia código, así que necesita despliegue con etiqueta (RDA-007). **Viaja con la 03-05**, junto con la 03-01, la 03-02 y la 03-04. Sin migraciones ni cambios de esquema.
- Respaldo previo: lo decide el desarrollador en la 03-05. La corrección de `estado_pago` solo toca filas cuando se edita un pedido o un pago, salvo que la decisión 6 sea B o C.
- Retroceso: volver a la etiqueta anterior (`docs/operacion/retroceso.md`); sin migraciones que deshacer.

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| El éxito falso de las ediciones pasa a un 500 y el formulario se pierde hasta la 03-04 | Viaja con la 03-05 junto con la 03-04. Los datos quedan íntegros: se revierte todo |
| R1, R2 y R4 fallan por el error y no por los datos | Ajustarlas primero y comprobar el motivo del fallo antes de corregir (paso 1) |
| Las pruebas de la 01-09 (`CapturasItemsTests`) y la caracterización del abono dejan de ser ciertas | Reescribirlas o retirarlas en la misma iteración, con la decisión que las respalda |
| La conversión cambia lo que ve el usuario si el abono es inválido y toca una plantilla | Decisión 3; leer `DESIGN.md`; revisión a 360 px |
| `estado_pago` se recalcula con la regla provisoria de $0 y de sobrepago | Usa el ayudante existente y el oráculo ya fijado; el `PENDIENTE_CLIENTE` sigue registrado; en `crear_pedido` solo se recalcula si hay abono |
| Una imagen subida queda huérfana al revertir | Decisión 2 (A recomendada); nunca borrar un archivo sin saber si otro pedido lo usa |
| Un `messages.*` nuevo no se ve | No se usan mensajes para avisos en esta iteración (decisiones 1 y 4) |
| Se mezcla con la 03-04 (mensajes y formulario), la 04-01 (POST) o la 07-02 (servicios) | La sección «Fuera de alcance» y las decisiones 1, 5 y 8 fijan el límite |
| La iteración es grande | Pasos ordenados con verificación propia; decisión 7 |
| Se toma `estado_pago` por un dato visible | La corrección no cambia lo que se ve hoy; el criterio es de datos y pruebas, no de pantalla |

## Decisiones del desarrollador

Todas resueltas el 2026-11-04, con la opción A (la recomendada):

1. **Propagar el error** (500, sin captura): las tres vistas de ítems quedan como `crear_pedido` desde la 03-02.
2. **Imágenes huérfanas:** aceptarlas y documentarlo en `despliegue.md` (sección 3.7).
3. **Formulario de la conversión con fecha, abono y estado.** **Reemplaza** la decisión del 2026-10-27 (D5 de la 02-04) que dejaba R18 y AUD-02-027 en la 03-04: pasan a esta iteración, con nota fechada en `pruebas.md`, `auditoria-tecnica.md` y `iteracion-02-04-regresiones.md`.
4. **Conversión repetida:** redirigir al detalle de la cotización, sin mensaje.
5. **AUD-02-028 (R19)** a la 04-01.
6. **No reparar** los `estado_pago` históricos (610 de 870 en la medición del 2026-10-20); queda anotado con la cifra.
7. **Una sola iteración.**
8. **El abono inicial que la edición descarta,** fuera de alcance; propuesta en la sección 4 de `registro-pendientes.md`.

Estado de la iteración: se usa «Pendiente (redactada)» mientras no se ejecuta (el README protegido no define «Redactada»).

## Datos requeridos del cliente

- Ninguno nuevo para ejecutar esta iteración.
- Siguen abiertos, sin cambiar de comportamiento aquí: valor de una cotización neto o con IVA (AUD-02-014), pedido de $0 como pagado y sobrepago (`registro-pendientes.md`, sección 2).
