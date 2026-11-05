# Bitácora 03-04 · Contrato de error hacia el usuario

- **Fecha:** 2026-11-04 (ejecución hasta el paso 4) y 2026-11-05 (pasos 5 a 10 y verificación)
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión. Falta la revisión manual del desarrollador. Sin despliegue propio: viaja con la 03-05. Sin commit.

## Resumen

Se ejecutó la iteración 03-04 en local con las diez decisiones del desarrollador del 2026-11-04 (la recomendada en todas; en la 3, la B con respuesta 200; en la 8, la C) y los textos aprobados literales. Los mensajes de error de Django ahora se ven; los formularios de pedido y cotización devuelven lo escrito (ítems y método de pago) ante un error de validación o un ítem que no se puede guardar; crear pedido, cotización y pago llevan un token de envío único en la sesión; los formularios de escritura bloquean el botón al enviar; y la página 500 pide pantalla y hora. R21 pasó de fallo esperado a verde. El token suma consultas por página: la ejecución se detuvo en el paso 4 por la sección 11 de `AGENTS.md` y el desarrollador aceptó el costo.

## Decisiones del desarrollador (2026-11-04)

1. Las diez decisiones de la iteración con la opción recomendada (en la 3, la B con respuesta 200; en la 8, la C). Detalle en [la iteración](../../10_epicas/epica-03-integridad-transaccional/iteracion-03-04-contrato-de-error-hacia-el-usuario.md).
2. Paso 7 aprobado: `text-red-600`, `role="alert"`, `aria-invalid`, `aria-describedby` y sin `animate-pulse`, solo en las plantillas que ya se tocan.
3. Textos aprobados, literales (ítem, formulario vencido, imagen y página 500).
4. **Costo de consultas aceptado:** la 5-A sigue tal como está (+3 consultas por cada GET y POST exitoso de crear pedido, cotización e ingresar pago; +1 real sin `BEGIN` y `COMMIT`). **Tope de 20 tokens confirmado.**
5. **Verificación a posteriori de `test_envio_unico.py`** antes del paso 5 (ver «Desviaciones»).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/envio_unico.py` | **Nuevo.** Token en la sesión: `emitir`, `estado`, `consumir`; tope de 20. |
| `pedidos/views.py` | `ERRORES_DE_ITEM` y textos; captura fuera del `atomic` en `crear_pedido`, `editar_pedido`, `crear_cotizacion` y `editar_cotizacion`; `items_json` y `metodo_pago` devueltos; aviso de imagen; token en `crear_pedido`, `crear_cotizacion` e `ingresar_pago`; texto de la restauración fallida sin `backups/`. |
| `pedidos/forms.py` | `ErroresAccesiblesMixin` (`aria-invalid` y `aria-describedby` en los campos con error) en cinco formularios. |
| `pedidos/templates/pedidos/base.html` | Bloque de mensajes: pinta solo `error` (`role="alert"`); recorre y descarta el resto. |
| `pedidos/templates/pedidos/pedido_form.html`, `cotizacion_form.html`, `pago_form.html` | Campo `token_envio`; errores accesibles (`id`, `role`, `text-red-600`), sin `animate-pulse`; el método de pago elegido queda marcado (pedido). |
| `pedidos/templates/pedidos/cliente_form.html`, `producto_form.html` | `data-bloquear-envio`; errores accesibles. |
| `pedidos/templates/pedidos/cotizacion_convertir.html`, `cliente_confirm_delete.html`, `cotizacion_confirm_delete.html`, `pedido_confirm_delete.html`, `producto_confirm_delete.html` | `data-bloquear-envio` (textos «Convirtiendo…» y «Eliminando…»). |
| `pedidos/templates/pedidos/restaurar_bd.html` | Bloquea el botón después de la confirmación de SweetAlert2 y lo recupera con `pageshow`. |
| `pedidos/templates/pedidos/errors/500.html` | Texto aprobado: pantalla y hora. |
| `pedidos/static/pedidos/js/index.js` | `bloquearBoton`, `desbloquearBoton`, `initBloqueoEnvio`. |
| `pedidos/tests/test_contrato_error.py`, `test_envio_unico.py`, `test_bloqueo_envio.py` | **Nuevos.** |
| `pedidos/tests/ayudas.py` | `token_de`, `con_token` y los textos aprobados literales. |
| `pedidos/tests/test_regresiones.py` | R21 (escrita como fallo esperado y retirada al pasar a verde). |
| `pedidos/tests/test_fronteras_transaccionales.py`, `test_pedidos.py` | Ítem fallido: de «500» a «formulario devuelto (200)», una línea `ERROR` de `pedidos.views`. |
| `pedidos/tests/test_cotizaciones.py`, `test_eventos_negocio.py` | `ejecutar` con token. |
| `pedidos/tests/test_capturas_amplias.py`, `test_errores.py` | Texto de la restauración sin `backups/`; texto de la 500; POST con token. |
| `docs/operacion/pruebas.md`, `docs/operacion/despliegue.md` | Archivos nuevos, R21 retirada, sección 9.1; sección 3.9 «Cuando un usuario reporta un error». |
| `_planificacion/…/iteracion-03-04-…md`, `definicion-epica-03.md`, `00_producto/registro-pendientes.md`, `auditoria-tecnica.md` | Estado, decisiones, criterios, resultado y notas fechadas. |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-04.md` | Esta bitácora (nueva). |

## Verificación

Todo con `DB_NAME=manzagrafica_replica` y el MySQL local de Docker; las pruebas usan `test_manzagrafica`. No se consultaron datos de la réplica.

| Comprobación | Resultado |
| :----------- | :-------- |
| Línea de partida (paso 0) | 220 pruebas, `OK (expected failures=9)` |
| R21 escrita antes de corregir | `OK (expected failures=10)` |
| Final, tres ejecuciones | 263 pruebas, `OK (expected failures=9)` las tres (288,7 s, 258,8 s y 284,3 s) |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |

La línea `RuntimeError: mysql falló` que aparece en la salida es de una prueba que simula ese fallo a propósito.

### Pruebas primero: qué falló antes y por qué

- **Mensajes visibles (paso 2):** 5 de 7 fallaban: sin el texto en el HTML de la pantalla de destino y la tarjeta de restauración con mensajes de pagos acumulados (`2 != 0` y `1 != 0`). Confirma el defecto latente inferido en la redacción.
- **Formulario conservado (paso 3):** `'[]' != '[{"producto_id":"1",…'` (editar cotización), ítems de la base en vez de los del usuario (editar pedido), 500 en vez de 200 en los ítems fallidos, falta el aviso de imagen.
- **Texto de la 500 (paso 6):** no estaba el texto aprobado.
- **Bloqueo (paso 5):** ningún formulario declaraba el atributo ni el JavaScript tenía las funciones.
- **Errores accesibles (paso 7):** 10 fallos (sin `id`, `role`, `aria-*`; `animate-pulse` y `text-red-500`).
- **R21:** escrita como fallo esperado (10). No se comprobó por separado que fallara por `2 != 1`; el motivo es que sin token los dos POST crean dos pedidos, y la misma situación sin token hace fallar 18 de 19 pruebas del mecanismo (abajo).

### Desviaciones

1. **Regla 15 en `test_envio_unico.py` (corregida a posteriori, por decisión del desarrollador).** Las pruebas del token se escribieron junto con la implementación, no antes. Verificación: se desactivó temporalmente el token en `crear_pedido`, `crear_cotizacion` e `ingresar_pago` (copia de seguridad de `views.py`, tres funciones de reemplazo) y se corrió el archivo. **Primera pasada:** 19 pruebas, 12 distintas fallaban y 7 pasaban: una es correcta (`test_los_formularios_de_edicion_no_llevan_token` afirma la ausencia del token) y **seis pasaban de forma trivial** (comprobaban que un token «se conserva» o «es distinto» cuando no había token). **Se endurecieron** esas seis (ahora afirman que el token existe) y en la **segunda pasada** fallan **18 de 19**: la que pasa es `test_los_formularios_de_edicion_no_llevan_token`, que afirma justo la ausencia del token. Las dos que daban `ERROR` lo hacían por `MultipleObjectsReturned: get() returned more than one Pedido -- it returned 2!` (los duplicados que el token debe evitar). Se restauró `views.py` y se comprobó que quedó **idéntico byte a byte** (`cmp`) y con el **mismo `git diff`** (dos veces, tras cada pasada).
2. **Prueba de la línea `INFO` del rechazo** (`test_el_rechazo_deja_una_linea_info…`) agregada junto con su código (`_avisar_formulario_vencido`), sin verla fallar antes. Existe porque `despliegue.md`, sección 3.9, promete esa línea.
3. **Detención en el paso 4** por el aumento de consultas (`AGENTS.md`, sección 11); reanudada con la decisión del desarrollador.
4. **Otros ajustes menores sin impacto en la decisión:** el primer intento de editar con un heredoc largo falló antes de aplicar nada (sin efecto); `index.js` quedó con finales de línea mezclados y se normalizó a CRLF.

## Consultas antes y después (regla 12)

Método de [bitacora-03-03-medicion](bitacora-03-03-medicion.md) en lo esencial: `CaptureQueriesContext` con `TransactionTestCase` (autocommit, como en producción), datos sintéticos, un `GET /clientes/lista/` de calentamiento y **dos vueltas** idénticas. «Antes» se midió con el código de la 03-03 (con las pruebas ya escritas pero antes de cambiar nada) y «después» con el código final; en el paso 4 y al final dieron lo mismo. Los POST llevan el token cuando el formulario lo trae. El archivo de medición era temporal y **se borró**.

| Petición | Antes | Después | Dif. | Sin `BEGIN` y `COMMIT`: antes → después | HTTP |
| :------- | ----: | ------: | ---: | :-------------------------------------- | :--- |
| GET `crear_pedido` | 4 | 7 | +3 | 4 → 5 | 200 → 200 |
| POST `crear_pedido` (abono, 2 ítems) | 16 | 19 | +3 | 14 → 15 | 302 → 302 |
| GET `crear_cotizacion` | 4 | 7 | +3 | 4 → 5 | 200 → 200 |
| POST `crear_cotizacion` | 11 | 14 | +3 | 9 → 10 | 302 → 302 |
| GET `ingresar_pago` (con pedido) | 6 | 9 | +3 | 6 → 7 | 200 → 200 |
| POST `ingresar_pago` | 13 | 16 | +3 | 11 → 12 | 302 → 302 |
| GET `lista_pagos` (recorre el bloque de mensajes) | 4 | 4 | 0 | 4 → 4 | 200 → 200 |
| GET `editar_pedido` (sin token) | 6 | 6 | 0 | 6 → 6 | 200 → 200 |

- **Origen (inferido por lectura, confirmado por la forma de la cifra):** Django guarda la sesión con `BEGIN`, `UPDATE`, `COMMIT`. Ocurre una vez al abrir cada formulario de creación (se emite el token) y otra al guardar con éxito (se consume).
- **El bloque de mensajes de `base.html` no suma consultas** (`lista_pagos` y `editar_pedido` no cambian).
- **No medido:** las vistas de ítem fallido, de envío repetido y de rechazo; el costo con muchos tokens (hay un tope de 20 por sesión).

## Hallazgos de la ejecución

1. **Después del token, los formularios devueltos por un fallo de ítem llevan el mismo token** (aún sin usar) y los rechazados por token, uno nuevo. Hay pruebas para ambos.
2. **Rebuild del formulario de creación tras el fallo:** el guardado llega a asignar un `pk` al objeto en memoria; si no se reconstruye el formulario, la pantalla diría «Editar Pedido». Hay pruebas para pedido y cotización.
3. **Un 500 no gasta el token** (el `SessionMiddleware` no guarda la sesión en 5xx, verificado en Django 6.0.1) y una prueba lo comprueba.
4. **Seis pruebas del mecanismo pasaban sin token** (ver desviación 1): una advertencia para las pruebas que verifican «se conserva X» sin comprobar antes que X existe.
5. **El tope de 20 tokens tiene una consecuencia práctica:** con más de 20 formularios de creación abiertos en la misma sesión, el más antiguo ya no sirve (se rechaza con el aviso de «venció» y los datos conservados).

## Contradicciones y puntos a revisar (sin corregir)

1. **`DESIGN.md:102` contra RDA-013.** Ver la propuesta abajo.
2. **`DESIGN.md` sección 8 y el giro del ícono.** `bloquearBoton` usa `animate-spin` (como la 00-06 y la 00-07), que la sección 8 no permite (solo transiciones de color y el giro del chevron; el resto es `PENDIENTE_DESARROLLADOR`). Ya estaba registrado para la 00-07; ahora son más pantallas.
3. **`animate-pulse` y `text-red-500` en plantillas no tocadas** (`dashboard.html`, `trabajo_semanal.html`, `producto_confirm_delete.html`): el paso 7 se limitó a las plantillas tocadas, como se aprobó.
4. **`views.py` importa `from PedidosApp import settings`** (regla 7 de `AGENTS.md` pide `django.conf.settings`). Preexistente; no se tocó. La prueba de la restauración parchea ese objeto.
5. **El rechazo por token deja una línea `INFO`.** Si la configuración de producción no emite `INFO` a `server.log`, `despliegue.md` 3.9 promete algo que no se verá. No se verificó en producción.
6. **`definicion-epica-03.md`:** los «03-04 sin redactar» de las líneas 7 y 64-65 se corrigieron con nota fechada y tachado; el estado de la épica sigue «Pendiente».
7. **Estados:** «En revisión» está en el README protegido; el estado de la épica no cambia.
8. **Otras salidas de error fuera del contrato** (JSON crudo en `index.js:254` y `:686`; página 403 por CSRF) siguen como propuestas del registro.
9. **Fechas de las notas:** parte del trabajo se hizo el 2026-11-04 y parte el 2026-11-05; las notas de las decisiones llevan el 2026-11-04 (día de las decisiones) y el cierre, el 2026-11-05.

### Propuesta de cambio a un documento protegido (no editado)

- **Archivo y sección:** `DESIGN.md`, sección 5 «Componentes», fila «Página de error» (`:102`).
- **Texto actual:** «Mensaje comprensible, sin detalles técnicos, con un identificador del error que el usuario puede informar y un enlace al panel de control.»
- **Texto propuesto:** «Mensaje comprensible, sin detalles técnicos, que pide informar en qué pantalla estaba el usuario y a qué hora, y un enlace al panel de control. No muestra un identificador del error (RDA-013).»
- **Por qué:** RDA-013 descartó el identificador y la página de la 01-03 y de la 03-04 no lo tienen. Si no se cambia, `DESIGN.md` exige algo que la aplicación no hace.
- **Pendiente relacionado:** la sección 5 no tiene una fila para el aviso de error de `base.html` (rojo, `role="alert"`, ícono `error_outline`); conviene describirlo ahí (color por nivel, foco). Se deja `PENDIENTE_DESARROLLADOR`. Tampoco define el estado «Guardando…» de los botones (ver contradicción 2).

## Migraciones

- Ninguna. `makemigrations --check --dry-run`: `No changes detected`.

## Revisión manual

Pasos 1 a 12, con comandos de PowerShell 7 y `runserver --insecure --nothreading`, en [la iteración](../../10_epicas/epica-03-integridad-transaccional/iteracion-03-04-contrato-de-error-hacia-el-usuario.md), sección «Revisión manual». Falta que el desarrollador la haga y la registre.

## Commit sugerido

`Épica 3 - Iteración 03-04: contrato de error con avisos visibles, formularios que conservan lo escrito, token de envío único, bloqueo del botón y R21 en verde`
