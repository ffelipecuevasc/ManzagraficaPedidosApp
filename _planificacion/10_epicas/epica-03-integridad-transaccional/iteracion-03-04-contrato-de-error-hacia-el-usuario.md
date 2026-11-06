# Iteración 03-04 · Contrato de error hacia el usuario

- **Épica:** 03 · Integridad transaccional
- **Estado:** Terminada (2026-11-06), con la excepción de la presentación del aviso rojo y del aviso de ítem fallido (AUD-05-006 y AUD-05-007, que quedan para la Épica 08). Ejecutada en local con las diez decisiones del desarrollador del 2026-11-04 (la recomendada en todas; en la 3, la B con respuesta 200; en la 8, la C) ([bitacora-03-04](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04.md)); revisión de servidor y corrección del abono el 2026-11-06 y revisión manual del desarrollador el mismo día ([bitacora-03-04-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-cierre.md)). Sin despliegue propio: viaja con la 03-05. Historial de estados: Pendiente (redactada el 2026-11-04, [bitacora-03-04-redaccion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-redaccion.md)) → En revisión (2026-11-04) → Terminada (2026-11-06).
- **Subfase del plan:** 3.4 «Contrato de error hacia el usuario» (`plan-de-trabajo.md:358-362`)
- **Depende de:** 03-03 (Terminada el 2026-11-04)
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-013 (errores con `logging` en `server.log`, sin identificador de correlación ni tabla de errores), RDA-019 (los errores de vista los maneja Django; la captura, si existe, va **fuera** del `atomic`).
- **Hallazgos que cierra:** AUD-04-001 en su parte de servidor (token de envío único, bloqueo del botón y R21); el hallazgo sigue abierto por la consulta histórica de duplicados (06-04) y el indicador de carga (08-07).
- **Hallazgos relacionados:** AUD-02-006 (**avance, no cierre**: la 01-09 ya dejó el texto fijo y el registro; esta iteración hace que el aviso se vea; el GET lo corrige la 04-01), AUD-02-008 (evidencia P3: «a veces al guardar sale error y no se guarda»), AUD-02-021 (**no se toca**: sin causa conocida).
- **Cambio de esquema:** Ninguno si la decisión 5 es A (sesión, recomendada). Clase 2 si es B o C; en ese caso se detiene y se consulta (`AGENTS.md`, secciones 6 y 11).
- **Respaldo previo al despliegue:** No lo exige por sí misma con la decisión 5-A (sin migraciones). Lo decide el desarrollador al planificar la 03-05.
- **Etiqueta y ventana:** sin despliegue propio; viaja con la 03-05, igual que la 03-01, la 03-02 y la 03-03.

## Objetivo

Que un error llegue al usuario de una forma única y predecible: si el dato está mal, vuelve al formulario con lo que escribió y el mensaje junto al campo; si falla el sistema, ve un mensaje fijo, comprensible y sin detalles técnicos, y la traza completa queda en `server.log`. Además, que un envío repetido no cree un segundo pedido, cotización o pago (alcance 4 y 6 de la épica).

## Cómo se lee este documento

- **Documentado:** está escrito en el repositorio o en la planificación; se cita archivo y línea (leídos el 2026-11-04).
- **Inferido:** sale de leer el código, no de ejecutarlo ni de verlo en pantalla. Se marca «(inferido)». Lo que la iteración puede confirmar con una prueba automática o en la revisión manual lo dice.
- Los textos de la sección «Textos aprobados» los aprobó el desarrollador el 2026-11-04, literales.

## Alcance contra la definición de la épica

Verificado contra `definicion-epica-03.md` (alcance 4 y 6, «Para la redacción de 03-04» y criterio de término) y `plan-de-trabajo.md:358-362`.

| Pieza | Fuente | En esta iteración |
| :---- | :----- | :---------------- |
| Errores de validación: volver al formulario con los datos conservados y el mensaje junto a cada campo | Alcance 4, primer punto | Sí (decisiones 3 y 4) |
| Errores del sistema: `logger.exception`, mensaje fijo (`messages.error`) o página 500 | Alcance 4, segundo punto | Sí (decisiones 1, 2 y 3) |
| Cómo se informa un error: pantalla y hora, sin identificador (RDA-013) | Alcance 4, tercer punto | Sí (texto de la página 500, mensajes fijos y `docs/operacion/`) |
| Ningún mensaje muestra `str(e)`, rutas del servidor ni salidas de `mysql` o `mysqldump` | Alcance 4, tercer punto; AUD-02-006 | Sí: inventario de los diez `messages.*` y decisión 9 |
| Peor caso: perder un formulario largo por un error del sistema | Alcance 4, cuarto punto | Sí (decisión 4) |
| Token de envío único en pedido, cotización y pago | Alcance 6; «Para la redacción de 03-04» | Sí (decisiones 5, 6 y 7) |
| Bloqueo del botón en todos los formularios de escritura | Alcance 6 | Sí (decisión 8) |
| Regresión R21 | Alcance 6; «Para la redacción de 03-04» | Sí |
| R18 (AUD-02-027) | — | **No:** se resolvió en la 03-03 (decisión 3-A) |
| Validación y despliegue con vigilancia | Alcance 5 | **No: 03-05** |
| Hallazgos de otras épicas (GET que escribe, plantilla de eliminar pago, fechas, servicios) | — | **No** (ver «Fuera de alcance») |

## Qué hace hoy (evidencia leída el 2026-11-04)

### Los mensajes de Django casi no se ven

`views.py` tiene diez llamadas a `messages.*`. Solo `restaurar_bd.html` recorre `messages` (`restaurar_bd.html:100-137`); ni `base.html` ni las demás plantillas lo hacen, aunque el procesador de contexto está activo (`settings.py:91`). **Además, esa plantilla pinta solo el nivel `success`** (`:102` abre un único `{% if message.tags == 'success' %}` que se cierra en `:134`, sin rama para `error` ni `warning`).

| Línea | Vista | Nivel | Texto | Redirige a | ¿Se ve? (inferido) |
| :---- | :---- | :---- | :---- | :--------- | :----------------- |
| `:916` | `convertir_a_pedido` | success | «Cotización convertida exitosamente en el Pedido #N» | `detalle_pedido` | No |
| `:1132` | `generar_respaldo_bd` | error | «No se pudo generar el respaldo. El detalle quedó en el registro del servidor.» | `respaldar_bd` | No |
| `:1146` | `restaurar_bd` | error | «No se seleccionó ningún archivo.» | `restaurar_bd` | No (no es `success`) |
| `:1153` | `restaurar_bd` | error | «Error: El archivo debe tener extensión .sql» | `restaurar_bd` | No |
| `:1179` | `restaurar_bd` | error | «Operación cancelada: no se pudo crear el respaldo de seguridad previo, así que la base no se tocó.» | `restaurar_bd` | No |
| `:1192` | `restaurar_bd` | success | «¡Éxito! La base de datos fue restaurada con el archivo: …» | `restaurar_bd` | **Sí** (tarjeta de éxito) |
| `:1206` | `restaurar_bd` | error | «La restauración falló. La base puede haber quedado restaurada en parte: …» | `restaurar_bd` | No |
| `:1406` | `ingresar_pago` | success | «Pago de $… registrado correctamente.» | `lista_pagos` | No |
| `:1441` | `editar_pago` | success | «Pago actualizado correctamente.» | `detalle_pedido` | No |
| `:1472` | `eliminar_pago` | warning | «Se eliminó el pago de $…» | `detalle_pedido` | No |

- **Los avisos de la 01-09 (respaldo y restauración) tampoco se ven.** La 01-09 dejó el texto fijo y el registro (opción C), pero ninguna pantalla muestra los de nivel error. Sus pruebas (`test_capturas_amplias.py:39-40`, `:46-91`) leen la cola con `get_messages(respuesta.wsgi_request)`: miden lo que la vista **encoló**, no lo que el usuario **ve**.
- **Defecto latente (inferido, no reproducido):** Django guarda la cola de mensajes (cookie y, si no cabe, sesión; clase por defecto verificada en Django 6.0.1) hasta que una plantilla la recorre. Como solo `restaurar_bd.html` lo hace, los mensajes `success` de pagos y conversión se acumulan, y el día que un superusuario abra esa pantalla cada uno se dibujaría como la tarjeta «¡Base de Datos Restaurada Exitosamente!» con el texto del pago (`restaurar_bd.html:114-119`). Una prueba automática lo confirma antes de corregir (paso 2).
- **Formato de los montos:** `:1406` y `:1472` escriben `${pago.monto}` sin separador de miles (`monto` es `PositiveIntegerField`, `models.py:93`): saldría «$15000», contra la regla 7.1 de `AGENTS.md` (`$15.000`). Hoy no se nota porque no se ve.

### Qué se pierde cuando el servidor devuelve el formulario con error

Los campos del formulario de Django se conservan (formulario ligado). Lo que no es campo de Django, no:

| Dato | `crear_pedido` | `editar_pedido` | `crear_cotizacion` | `editar_cotizacion` |
| :--- | :------------- | :-------------- | :----------------- | :------------------ |
| Ítems (`items_json`) | **Se pierden.** El contexto no lo incluye (`views.py:238-244`) y la plantilla escribe `{{ items_json\|default:'' }}` (`pedido_form.html:268-269`) | **Se reemplazan por los de la base** (`:286-302`): se pierden los cambios | **Se pierden** (`:776-781`; `cotizacion_form.html:264-265`) | **Se reemplazan por los de la base** (`:815-833`) |
| Método de pago | El `<select name="metodo_pago">` no marca ninguna opción (`pedido_form.html:401-407`): vuelve a «Efectivo» (inferido) | No aplica | No aplica | No aplica |
| Imagen de referencia | El navegador no vuelve a rellenar un campo de archivo (limitación conocida de HTML, no verificada aquí) | Igual | No aplica | No aplica |

- **Consecuencia (inferida):** un error de validación (por ejemplo, fecha mal escrita) en un pedido con 10 ítems devuelve el formulario **sin los 10 ítems**. El criterio de término de la épica («un error de validación en la creación o edición de un pedido devuelve el formulario con los datos ingresados») no se cumple hoy.
- **Precedente en el repositorio:** la conversión de la 03-03 ya conserva lo escrito y el método de pago (`cotizacion_convertir.html:51` y `:74`; `ConversionFormularioTests.test_la_pagina_conserva_lo_que_escribio_el_usuario`).
- **Cómo carga el navegador los ítems:** `index.js:418-427` lee `#input-items-json` y dibuja la tabla; si el JSON no se puede leer, deja un `console.error` y la tabla vacía.

### Qué ve el usuario cuando falla el sistema

- **Una excepción que sale de una vista de escritura** responde la página 500 (`errors/500.html`) y deja **una** línea `django.request` con traza, método, ruta y usuario (03-01 y 03-03; `test_errores.py`, `test_fronteras_transaccionales.py`). Hasta esta iteración, **un ítem fallido muestra esa página y el formulario se pierde.**
- **El texto de la página 500** dice «Si el problema sigue, avísale al administrador y cuéntale qué estabas haciendo» (`500.html:18-20`): pide qué hacía, no a qué hora. La épica pide pantalla y hora (alcance 4).
- **Las vistas ya no capturan excepciones de ítems** (03-02 y 03-03). Las únicas capturas amplias que quedan en `views.py` son las de respaldo y restauración (`:1129`, `:1173`, `:1198`), todas con `logger.exception` y texto fijo (01-09).
- **El diagnóstico existe:** `docs/operacion/despliegue.md:255-262` trae el filtro `grep "ruta=/la/ruta/" $L | sed 's/#012/\n/g'`. No hay una sección que diga «un usuario reportó un error: qué pregunto y cómo busco» (inferido, por búsqueda de `ruta=` en `docs/operacion/`).
- **Endpoints JSON de creación rápida** (`api_crear_cliente_rapido` `:626-640`, `api_crear_producto_rapido` `:1042-1065`): devuelven `{"success": false, "errors": …}` con los errores del formulario, como pide `AGENTS.md`, sección 9. El JavaScript los muestra como `'Error: ' + JSON.stringify(data.errors)` (`index.js:254`) y con `alert("Error: " + JSON.stringify(...))` (`index.js:686`): el usuario ve JSON crudo. No es un detalle técnico del sistema, pero tampoco es un mensaje comprensible. **No entra en esta iteración** (ver «Fuera de alcance»).
- **Fallo de CSRF y sesión vencida:** `urls.py:32-33` define solo `handler404` y `handler500`, y `errors/` solo tiene `404.html` y `500.html`. Django usa por defecto su vista `csrf_failure` (verificado en `global_settings`). Un formulario que falla por CSRF mostraría la página 403 de Django, fuera del contrato y con el formulario perdido (inferido). **No entra en esta iteración.**

### Envío único y bloqueo del botón

- **Servidor:** nada rechaza un envío repetido. Medido en producción (AUD-04-001): dos `POST /pedidos/nuevo/` con menos de 0,3 s entre ambos crearon dos pedidos (2026-10-27).
- **Navegador:** solo `pedido_form.html` (script en línea, `:432-464`, 00-07) y `login.html` (00-06) bloquean el botón. Los demás formularios de escritura no:

| Plantilla | Formulario | Bloqueo hoy |
| :-------- | :--------- | :---------- |
| `pedido_form.html:30` | Crear y editar pedido | Sí (00-07, script en línea) |
| `cotizacion_form.html:31` | Crear y editar cotización | No |
| `pago_form.html:52` | Registrar y editar pago | No |
| `cotizacion_convertir.html:40` | Convertir cotización | No |
| `cliente_form.html:35`, `producto_form.html:35` | Crear y editar cliente y producto | No |
| `cliente_confirm_delete.html:34`, `cotizacion_confirm_delete.html:32`, `pedido_confirm_delete.html:34`, `producto_confirm_delete.html:52` | Confirmar eliminación | No |
| `restaurar_bd.html:36` | Restaurar la base (SweetAlert2 y luego `submit()`, `:61-80`) | No |
| `base.html:237` | Cerrar sesión | No |
| `registration/login.html:85` | Acceso | Sí (00-06) |
| `index.js:224` y `:637` | Creación rápida de cliente y producto (fetch) | Sí (deshabilita su botón) |

- **`DESIGN.md`, sección 5.1:** «Un botón que envía un formulario se deshabilita después del primer clic para evitar envíos dobles». Es regla vigente.
- **Sesiones (verificado en Django 6.0.1):** `settings.py` no define `SESSION_ENGINE`; el valor por defecto es `django.contrib.sessions.backends.db` (tabla `django_session`) con 1.209.600 segundos de vida (14 días). El `SessionMiddleware` **no guarda la sesión en respuestas 5xx** (`if response.status_code < 500`, en el código instalado). Cualquier mecanismo de token en la sesión hereda esa propiedad: un 500 no consume el token.
- **Un solo worker:** `AGENTS.md`, regla 8.10. Las peticiones corren en serie, así que dos POST seguidos no se solapan en producción (inferido). `runserver` local, en cambio, atiende con hilos: la prueba manual de doble envío usa `--nothreading`.
- **Pruebas:** 67 líneas de `pedidos/tests/` mencionan las rutas de creación (búsqueda por texto; incluye GET). Si la decisión 7 es A (rechazar sin token), las pruebas que hacen POST sin pasar por el formulario deben aprender a traer el token.

### Lo que `DESIGN.md` dice y lo que no

- **No define el componente de aviso** (mensaje de Django): la sección 5 no lo lista; los colores por estado y el estilo de foco son `PENDIENTE_DESARROLLADOR` (secciones 2.2 y 5.1). Un aviso nuevo usa solo tokens documentados (peligro `red-600`, textos slate); lo que falte se marca, no se inventa.
- **Contraste:** `DESIGN.md:58` documenta blanco sobre `red-600` en 4,83:1 (AA); ese es también el de `red-600` como texto sobre blanco. Las plantillas de pedido usan `text-red-500 text-xs` para el error junto al campo (`pedido_form.html:288`, 9 coincidencias de `text-red-500` en esa plantilla, 6 en `cotizacion_form.html`, 3 en `pago_form.html`). Por cálculo de la redacción con la fórmula de WCAG (no medido con herramienta), `red-500` sobre blanco da 3,76:1, bajo el 4,5:1 que `AGENTS.md`, regla 8.17, exige a texto pequeño. La 03-03 usó `text-red-600` en la conversión (`cotizacion_convertir.html:56`, `:79`).
- **Movimiento:** el aviso de error de `pedido_form.html:34` lleva `animate-pulse`, que la sección 8 no permite (solo transiciones de color y el giro del chevron; el resto es `PENDIENTE_DESARROLLADOR`). Un aviso nuevo no copia ese efecto.
- **Contradicción con RDA-013:** `DESIGN.md:102` dice que la página de error lleva «un identificador del error que el usuario puede informar». RDA-013 y el alcance 4 lo descartan, y `500.html` no lo tiene. Ver la propuesta en la bitácora de redacción (documento protegido, no se edita).

### Pruebas que esta iteración toca

| Prueba | Lugar | Hoy | Qué cambia |
| :----- | :---- | :-- | :--------- |
| `CapturasRespaldoTests` (4) | `test_capturas_amplias.py:43-91` | Afirman la cola `get_messages` | Se mantienen. Se suman pruebas que **renderizan** la pantalla de destino y afirman que el texto aparece |
| Ítem fallido en editar pedido, crear y editar cotización (cinco causas) | `test_fronteras_transaccionales.py:75-222` | Afirman 500 y datos intactos | Cambian solo si la decisión 3 es B o C |
| `CrearPedidoItemFallidoTests` | `test_pedidos.py` | Afirman 500 | Idem |
| Página 500 sin detalles técnicos | `test_errores.py:95-106` | Afirma «Algo salió mal» y que no hay detalles | Se mantiene; se suma la comprobación del texto nuevo (paso 6) |
| `test_creacion_de_pedido_invalida_registra_solo_nombres_de_campos` | `test_errores.py:120-127` | Verde | Se mantiene |
| Pruebas de creación de pedido, cotización y pago por POST | `test_pedidos.py`, `test_cotizaciones.py`, `test_pagos.py` y otras | Verdes, sin token | Cambian si la decisión 7 es A |
| **R21 (nueva)** | `test_regresiones.py` | No existe | Fallo esperado; pasa a verde con el token |

**Trampa conocida (03-02):** una excepción que sale de la vista sale también por el cliente de pruebas salvo `raise_request_exception = False`.

## Decisiones

**Resueltas el 2026-11-04** (sección «Decisiones del desarrollador»): la opción recomendada en las diez; en la 3, la B con respuesta 200, y en la 8, la C. Las opciones se conservan como constancia de lo evaluado. Dependencias entre ellas: la 1 condiciona la 2, la 6 (opción B) y la 7; la 3 y la 4 se resuelven juntas; la 5 condiciona la 6 y la 7.

### Decisión 1 · Dónde se muestran los mensajes de Django

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Bloque común en `base.html` (recomendada)** | Un solo bloque que recorre `messages` encima de `{% block content %}` (`base.html:262-264`), con `role="alert"` para errores y `role="status"` para el resto | Un solo lugar. Los avisos de respaldo y restauración (01-09) por fin se ven. Cualquier `messages.*` futuro se ve. Recorrer la cola la consume, lo que corrige el acarreo hacia `restaurar_bd` | Toca la plantilla base de **todas** las pantallas: revisión a 360 px, claro y oscuro. `restaurar_bd.html` dibuja su propia tarjeta de éxito: hay que evitar que se vea dos veces. `DESIGN.md` no define el componente (solo tokens documentados) |
| **B. Bloque en cada plantilla de destino** | Copiar el recorrido en `respaldar_bd.html`, `restaurar_bd.html`, `detalle_pedido`, `lista_pagos`… | Cambio local; no toca la base | Una copia por plantilla. Un `messages.*` nuevo hacia otra pantalla vuelve a no verse (el defecto actual). La cola se sigue acumulando donde no se recorre |
| **C. Aviso con SweetAlert2 desde `base.html`** | Un script convierte los mensajes en un modal o aviso | Patrón ya usado en `restaurar_bd.html:61`. La librería ya se carga (`base.html:316`) | Depende de JavaScript y de un CDN que la 08-07 retira: si el CDN falla, el aviso no aparece justo cuando hay un error. Un modal interrumpe. Accesibilidad y 360 px por revisar |

### Decisión 2 · Qué se hace con los avisos que ya existen y hoy no se ven

Cuatro no son de error: `:916`, `:1406`, `:1441` y `:1472`. Si el bloque común (decisión 1) los muestra, aparecen por primera vez en producción.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Mostrar solo los de error; consumir los demás sin mostrarlos (recomendada)** | El bloque pinta `error`; recorre y descarta el resto | Mínimo para el contrato (alcance 4 habla de errores). No cambia lo que el usuario ve en pagos y conversión. Corrige el acarreo hacia `restaurar_bd`. La tarjeta de éxito de `restaurar_bd` no se duplica | Cuatro llamadas siguen escribiendo mensajes que nadie ve. Un aviso informativo nuevo (decisión 6, opción B) tendría que ser de nivel error |
| **B. Mostrar todos los niveles y corregir los textos al formato `$15.000`** | Se ven todas las confirmaciones | Las llamadas ya estaban escritas para verse. Mejor respuesta al usuario | Cambia lo que se ve en cuatro flujos de producción sin que la épica lo pida. Hay que resolver el duplicado con la tarjeta de `restaurar_bd`. Textos nuevos que aprobar |
| **C. Retirar las cuatro llamadas** | Se borran `messages.success` y `messages.warning` | Elimina código sin efecto | Pierde confirmaciones que el cliente podría querer. Decide por el producto, no por el contrato de error |

### Decisión 3 · Qué pasa cuando un ítem no se puede guardar (pedido y cotización)

Causas medidas por las pruebas (`test_fronteras_transaccionales.py:63-71`): producto inexistente, JSON inválido, clave ausente, cantidad no numérica y precio no numérico.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Dejar la página 500, como hoy** | No cambia nada | Una sola forma de fallar. Sin captura nueva (regla 8.4) | El formulario se pierde: es el «peor caso a evitar» de la épica. El cliente ya reportó «a veces al guardar sale error y no se guarda» (P3) |
| **B. Capturar las excepciones concretas fuera del `atomic`, registrar y devolver el formulario con los ítems (recomendada)** | `try: with transaction.atomic(): … except (json.JSONDecodeError, KeyError, TypeError, ValueError, Producto.DoesNotExist):` con `logger.exception(…, extra={'request': request})` y un mensaje fijo. Cualquier otra excepción sigue yendo a la página 500 | Cumple el «peor caso». La captura fuera del bloque respeta la regla 3 y RDA-019. Cada fallo deja su traza en `server.log` | Fija una lista de excepciones. Es la opción que el desarrollador no eligió en la 03-02 (D) ni en la 03-03 (1-B), porque el aviso no se veía y faltaba este contrato; depende de las decisiones 1 y 4. Un `ValueError` de otro origen quedaría como aviso amable (pero registrado) |
| **C. Validar los ítems antes de abrir el `atomic`** | Una función que revisa cada ítem y devuelve errores por ítem, sin excepciones | Errores junto al ítem. No depende de capturas | Más código y reglas nuevas (qué es válido, por ejemplo cantidad 0 o negativa: `PENDIENTE_CLIENTE`). Valida el precio solo en su formato; validarlo contra el catálogo o recalcularlo está **prohibido** (`pruebas.md`, sección 9). La 07-02 lo moverá a servicios |

**Dentro de B o C: código de estado al devolver el formulario.** (i) 200, como cualquier formulario inválido (recomendado: `server.log` registra el `ERROR` igual); (ii) 500 con la plantilla del formulario, para que el fallo cuente en `access.log`. Se decide junto con la opción.

### Decisión 4 · Qué se conserva cuando el servidor devuelve un formulario con error, y cómo

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Desde el servidor: devolver `items_json` y `metodo_pago` del POST (recomendada)** | En las cuatro vistas (crear y editar pedido y cotización), el contexto lleva lo que llegó. Si el formulario traía imagen, un aviso fijo pide elegirla otra vez | Una prueba automática lo comprueba (criterio de término). Sin JavaScript nuevo. Mismo patrón que la conversión (03-03) | Se escribe en el HTML un JSON que vino del navegador: el autoescape de Django lo protege y una prueba con comillas y `<` lo confirma. Si el JSON llegó corrupto, la tabla queda vacía (`index.js:424-426`). No cubre un 500 inesperado |
| **B. Además, un borrador en el navegador (`sessionStorage`)** | El JavaScript guarda el formulario mientras se edita y lo restaura al volver | Cubre también el 500 inesperado, donde el servidor no puede devolver el formulario | JavaScript nuevo en `index.js` (801 líneas). Datos del cliente en el almacenamiento del navegador, con reglas de limpieza. Más revisión manual. Va más allá de «cuando sea posible» (alcance 4) |
| **C. Solo lo que Django ya conserva** | Sin cambios | Nada que hacer | Los ítems y el método de pago se pierden. No cumple el criterio de término si «datos ingresados» incluye el detalle |

### Decisión 5 · Mecanismo del token de envío único (AUD-04-001)

La definición de la épica dice «sin dependencias nuevas ni tabla nueva si basta la sesión; si exige tabla, Clase 2 con retención».

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Token en la sesión (recomendada)** | Al abrir el formulario se genera un token (`uuid4`), se guarda en la sesión (con tope de cuántos se conservan, valor por definir en la ejecución) y viaja en un campo oculto. Al guardar con éxito se consume y se anota a qué registro correspondió | Sin tabla, sin migración, sin dependencia, sin purga que implementar (regla 11). Un 500 no consume el token (la sesión no se guarda en 5xx). Con un solo worker las peticiones van en serie | Cada GET del formulario modifica la sesión: **consultas extra por página** (`AGENTS.md`, sección 11: detenerse si aumentan). No protege si algún día hay más de un worker (carrera entre dos lecturas de la sesión). Expira con la sesión |
| **B. Tabla nueva de tokens** | Una tabla con el token, la fecha y el registro creado | Sobrevive a la sesión. Auditable | Clase 2: migración, consulta previa y RDA. Exige retención y **purga en la misma iteración** (regla 11), pero la orden de mantención diaria llega en la 06-02. Escribe en MySQL en cada GET del formulario |
| **C. Columna con restricción única en cada modelo** | `token_envio` (nulo, único) en `Pedido`, `Cotizacion` y `Pago` | La única opción que garantiza el rechazo aunque haya varios workers. Sin tabla aparte | Clase 2 sobre tres tablas con datos vivos (índice único): respaldo previo y ensayo en la réplica. Guarda un dato técnico en cada registro. Consulta previa |

### Decisión 6 · Qué ve el usuario ante un envío repetido (token ya usado)

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Redirigir al registro ya creado, sin mensaje (recomendada)** | Mismo destino que el éxito: `detalle_pedido`, `detalle_cotizacion` o `lista_pagos` | Coherente con la conversión repetida de la 03-03 (decisión 4-A). No depende de los mensajes. Para el usuario, el doble clic «simplemente funcionó» | No explica por qué. Exige recordar qué registro creó cada token (más datos en la sesión) |
| **B. Redirigir con un aviso fijo («Este formulario ya se guardó…»)** | Igual, con texto | Explica | Depende de las decisiones 1 y 2: con la 2-A (solo errores) el aviso no se vería |
| **C. Redirigir a la lista** | Al listado de pedidos, cotizaciones o pagos | No hay que recordar el registro | El usuario no ve lo que creó; en pagos coincide con A |

### Decisión 7 · POST sin token, con un token que no es de esta sesión o vencido

Importa por el despliegue: los formularios abiertos antes de la 03-05 no traen token.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Rechazar, devolver el formulario con los datos conservados y un mensaje fijo (recomendada)** | No crea nada; el usuario vuelve a guardar con un token nuevo | Protege siempre. R21 («dos POST idénticos») se comprueba con el token del GET. Con la decisión 4-A no pierde nada | Cada formulario abierto durante el despliegue tiene que enviarse dos veces una vez. Las pruebas que hacen POST sin token se adaptan (67 líneas mencionan las rutas). Depende de las decisiones 1 y 4 |
| **B. Aceptar y dejar un `logger.warning`** | Compatible con todo lo anterior | Nada se rompe en el despliegue ni en las pruebas | Un POST sin token no queda protegido. Si R21 se escribe con dos POST **sin** token, seguiría fallando |
| **C. Rechazar con una página de error (403 o 400)** | Respuesta de error | Simple | El formulario se pierde: contra el alcance 4. Hoy no hay plantilla propia para 403 (ver «Qué hace hoy») |

### Decisión 8 · Cómo se bloquea el botón en los formularios de escritura

Inventario en la sección «Envío único y bloqueo del botón». Quedan fuera por decisión de la épica el acceso (00-06) y la creación rápida (ya bloquean). Si el cierre de sesión (`base.html:237`) cuenta como «de escritura» se decide aquí; se recomienda dejarlo fuera porque no escribe datos del negocio.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Repetir el script en línea de la 00-07 en cada plantilla** | Una copia por formulario | Patrón conocido y desplegado | Diez copias. Los scripts en línea chocan con la política de contenido estricta (08-08) |
| **B. Una función en `index.js` activada por un atributo (`data-bloquear-envio`) y migrar también `pedido_form.html`** | Un solo lugar, atributo en cada `<form>` | Una sola implementación, sin script en línea | Toca la corrección de la 00-07 (AUD-04-001, alta), cuya medición en `access.log` cae el 2026-11-11, antes de cualquier despliegue de esta iteración. Riesgo de regresar el defecto que esa iteración corrigió |
| **C. Función común en `index.js` para los demás; `pedido_form.html` conserva su script de la 00-07 (recomendada)** | Igual que B, sin tocar la 00-07 | No toca lo ya validado en producción | Quedan dos mecanismos para lo mismo hasta que la 08-03 (parciales) los una. `restaurar_bd.html` bloquea después de la confirmación de SweetAlert2 |

### Decisión 9 · Texto del fallo de la restauración (alcance 4: «ni rutas del servidor»)

`views.py:1201-1205` termina con «Está en la carpeta backups/ del servidor.» El nombre del archivo es generado por la aplicación; `backups/` es una carpeta relativa del servidor.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Quitar la mención de la carpeta y dejar el nombre del archivo (recomendada)** | «El respaldo de seguridad previo es respaldo_….sql.» | Cumple la letra de «ni rutas del servidor». El listado de respaldos de la pantalla ya muestra los archivos | Cambia un texto que la 01-09 validó. Se ajusta `test_restauracion_fallida_nombra_el_respaldo_previo` |
| **B. Dejarlo como está** | Sin cambios | Texto ya validado; indica dónde buscar | Nombra una carpeta del servidor, lo que el alcance 4 dice evitar |

### Decisión 10 · Una iteración o dos

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Una sola, con pasos ordenados (recomendada)** | Esta iteración, con un bloque de verificación por paso | La definición de la épica la trata como una pieza (alcance 4 y 6). Mismo criterio que la 03-03 (decisión 7-A). Sin despliegue propio | Es grande: base de plantillas, cuatro vistas de formulario, tres de token y diez plantillas de bloqueo. Mezcla dos propósitos (contrato de error y envío único) que `AGENTS.md`, sección 10, pide no mezclar entre fases, aunque aquí son de la misma fase |
| **B. Dividir: 03-04 (contrato de error) y una nueva con el envío único** | Dos iteraciones | Revisiones más chicas | Obliga a un número nuevo (03-06, porque 03-05 es el despliegue) y a reordenar la tabla de la épica. Ambas viajan juntas con la 03-05 |

## Textos aprobados (2026-11-04, literales)

Voz de `DESIGN.md`, sección 10: español de Chile, trato de tú, sin términos técnicos. Están en `views.py` (`TEXTO_ITEM_FALLIDO`, `TEXTO_IMAGEN`, `TEXTO_FORMULARIO_VENCIDO`), en `errors/500.html` y, literales, en `pedidos/tests/ayudas.py`.

| Uso | Propuesta |
| :-- | :-------- |
| Ítem que no se pudo guardar (decisión 3-B) | «No pudimos guardar el detalle de productos. Lo que escribiste sigue en pantalla: revísalo y vuelve a guardar. Si el problema sigue, avisa en qué pantalla estabas y a qué hora.» |
| Formulario vencido (decisión 7-A) | «Este formulario venció y no se guardó. Revisa los datos y vuelve a guardar.» |
| Aviso de imagen (decisión 4-A) | «Vuelve a elegir la imagen de referencia: el navegador no la conserva.» |
| Página 500 (`500.html:18-20`) | «Si el problema sigue, avísale al administrador y cuéntale en qué pantalla estabas y a qué hora.» |
| Respaldo, restauración (existentes) | Sin cambios, salvo la decisión 9 |

## Tareas (en este orden, una vez tomadas las decisiones)

Todo con `DB_NAME=manzagrafica_replica` y el MySQL local de Docker encendido. Cada paso empieza por la prueba (regla 15 de `AGENTS.md`) y termina con las pruebas del dominio en verde. Las plantillas se tocan después de leer `DESIGN.md`.

0. **Línea de partida:** `python manage.py test pedidos` → 220 pruebas, `OK (expected failures=9)` (medido al cierre de la 03-03; reconfirmar). **Medir las consultas** de las vistas que se tocan, con el método de [bitacora-03-03-medicion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-03-medicion.md) (`TransactionTestCase`, mismos datos antes y después). Si el token en la sesión aumenta las consultas por página, es un motivo para detenerse y consultar (`AGENTS.md`, sección 11).
1. **Aprobar los textos** de la tabla anterior y fijar el mapa de qué mensaje sale en cada caso.
2. **Mensajes visibles (decisiones 1 y 2).** Primero las pruebas: (a) un mensaje de error de respaldo o restauración aparece en el HTML de la pantalla de destino (hoy no); (b) tras registrar un pago, abrir `restaurar_bd` **no** muestra la tarjeta de éxito (confirma o descarta el defecto latente); (c) el texto técnico de `TEXTO_TECNICO` (`test_capturas_amplias.py:23`) no aparece en ninguna respuesta. Luego el bloque de `base.html` y, si hace falta, el ajuste de `restaurar_bd.html`.
3. **Conservar el formulario (decisiones 3 y 4).** Pruebas primero: crear y editar pedido y cotización con un dato inválido devuelven los ítems y el método de pago del POST; con comillas y `<` en el JSON no se rompe el HTML. Si la decisión 3 es B o C, las cinco causas de ítem fallido devuelven el formulario con el aviso, una línea `ERROR` con traza y nada escrito; si es A, las pruebas de la 03-03 quedan iguales.
4. **Envío único (decisiones 5, 6 y 7).** Primero **R21** como fallo esperado (`expected failures=10`): GET del formulario, dos POST con el mismo token, un solo pedido. Luego el mecanismo en `crear_pedido`; después `crear_cotizacion` e `ingresar_pago`, con pruebas normales (no son regresiones). El token se consume **después** de confirmar la transacción; un formulario devuelto por error lleva su token vigente.
5. **Bloqueo del botón (decisión 8)** en los formularios del inventario, con el estado «Guardando…» del patrón de la 00-06 y la 00-07 y la recuperación con `pageshow` al volver con «atrás».
6. **Cómo informar un error:** texto de `500.html` y sección en `docs/operacion/` («un usuario reportó un error»: pantalla y hora → filtro por ruta y hora en `server.log`, con el comando de `despliegue.md:255-262`). Sin identificador (RDA-013).
7. **Contraste y foco de los textos tocados:** los errores junto al campo de las plantillas que esta iteración modifica usan el patrón de `cotizacion_convertir.html` (`text-red-600`, `role="alert"`, `aria-invalid`, `aria-describedby`). El desarrollador confirma este paso al aprobar la redacción (ver «Riesgos»).
8. **Cierre técnico:** quitar `@expectedFailure` y `@tag('regresion')` de R21, dejar `expected failures=9` y actualizar `docs/operacion/pruebas.md` (valor vigente, fila retirada, sección de flujos). Comprobar que `despliegue.md`, paso 1, sigue remitiendo a `pruebas.md` para el número.
9. **Verificación:** `python manage.py test pedidos` en tres ejecuciones, `check`, `makemigrations --check --dry-run` y revisión manual (más abajo).
10. **Cierre documental:** bitácora, registro, notas fechadas en AUD-04-001, AUD-02-006 y AUD-02-008. Aplicar «Resuelto en 03-04» solo si las pruebas verdes lo respaldan.

## Regresiones que pasan a verde (predicción por lectura)

| Regresión | Hallazgo | Paso | Pasa a verde |
| :-------- | :------- | :--: | :----------- |
| R21 (nueva) | AUD-04-001 | 4 | Siempre. Se escribe como fallo esperado antes de corregir: los fallos esperados suben de 9 a **10** y bajan a **9** al terminar |

Quedan las nueve de la 04-01, 04-06, 06-01 y 07-02 (R6a, R6b, R6c, R7, R8, R9, R14, R15, R19). R5, R16 y R17 no se reasignan.

## Criterios de aceptación

- [x] Las decisiones 1 a 10 están registradas antes de implementar (2026-11-04; sección «Decisiones del desarrollador»).
- [x] Las pruebas se escribieron antes de la corrección, con **dos desviaciones declaradas** (ver el resultado de la ejecución): las de `test_envio_unico.py` se escribieron junto con la implementación y se verificaron a posteriori apagando el token (18 de 19 fallan), y la prueba de la línea `INFO` del rechazo se agregó junto con su código. Las demás fallaban por la razón correcta: mensajes sin el texto en el HTML y tarjeta de restauración con mensajes acumulados (`2 != 0`), ítems no devueltos (`'[]' != …`), texto de la 500, bloqueo sin atributo, errores sin `id` ni `aria-*`. R21 se escribió como fallo esperado (`expected failures=10`).
- [x] Los mensajes de error de respaldo y restauración **se ven** en su pantalla de destino (`MensajesDeErrorSeVenTests`, renderizan); ninguna respuesta contiene `str(e)`, rutas del servidor ni salidas de `mysql` o `mysqldump`.
- [x] Los mensajes de pagos y conversión no se acumulan ni aparecen en `restaurar_bd` (decisión 2-A; `AvisosQueNoSonDeErrorTests`).
- [x] Un error de validación en la creación o edición de un pedido y de una cotización devuelve el formulario con los datos ingresados, incluidos los ítems y el método de pago (`FormulariosConservanLoEscritoTests`; criterio de término de la épica).
- [x] Un ítem fallido (cinco causas) devuelve el formulario con los ítems y el aviso fijo (200, decisión 3-B), con una sola línea `ERROR` de `pedidos.views` con traza, método, ruta y usuario, y sin dejar nada escrito, en las cuatro vistas.
- [x] Dos POST con el mismo token crean un solo pedido, una sola cotización y un solo pago, y el segundo termina donde terminó el primero, sin mensaje (decisión 6-A; `EnvioRepetidoTests`).
- [x] R21 en verde y sin marcas; `python manage.py test pedidos` → `OK (expected failures=9)` en tres ejecuciones (ver la bitácora).
- [x] Los formularios del inventario declaran el bloqueo del botón (`data-bloquear-envio`, decisión 8-C) y `pedido_form.html` conserva su script de la 00-07 (`test_bloqueo_envio.py`). El comportamiento en el navegador (bloqueo, «Guardando…» y recuperación con «atrás») se comprueba en la revisión manual.
- [x] La página 500 y los avisos piden pantalla y hora, sin identificador (RDA-013); `docs/operacion/despliegue.md`, sección 3.9, explica cómo buscar la traza.
- [x] Sin `print`, sin `except Exception` nuevo en vistas de formulario, y toda captura nueva con excepciones concretas (`ERRORES_DE_ITEM`) fuera del `atomic` y `logger.exception(…, extra={'request': request})`.
- [x] Consultas antes y después registradas en la bitácora (regla 12). Aumentan en +3 por GET y POST de crear pedido, cotización y pago; el desarrollador lo aceptó el 2026-11-04 (decisión 1 de la ejecución).
- [x] `check` limpio y `makemigrations --check --dry-run` sin cambios (con la decisión 5-A), ver la bitácora.
- [x] Revisión manual hecha (más abajo). La hizo el desarrollador el 2026-11-06 contra la réplica local (dato dicho por él, no verificado por el agente): pasos 1 a 6 y 8 a 12 OK; el 7 lo cubrió la [revisión de servidor](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-revision-servidor.md). **Excepción declarada:** la presentación del aviso rojo (AUD-05-006) y del aviso de ítem fallido (AUD-05-007), que se resuelven en la Épica 08.
- [x] Los `PENDIENTE_CLIENTE` (AUD-02-014, valor $0 y sobrepago) siguen abiertos y sin cambios de comportamiento (no se tocó el precio del ítem ni el valor de venta).

## Revisión manual (la hace el desarrollador, contra la réplica local)

Con `DEBUG=False` y `runserver --insecure --nothreading` (un solo hilo, como el worker real), en escritorio y a 360 px (F12, modo dispositivo, ancho 360). Cada prueba en modo claro y, al menos una vez, en oscuro. Los pedidos, cotizaciones y pagos de prueba quedan en la réplica y se limpian al refrescarla al cierre de la Épica 03 (AUD-05-002).

**Preparación (PowerShell 7):**

```powershell
cd "D:\Trabajo\Proyectos PYTHON\Proyectos Personales\Pedidos Manzagrafica\PedidosApp"
.\.venv\Scripts\Activate.ps1
docker compose up -d                      # solo si el contenedor MySQL no está encendido
$env:DB_NAME = 'manzagrafica_replica'
$env:DEBUG = 'False'
python manage.py runserver --insecure --nothreading
```

Abre `http://127.0.0.1:8000/` con tu usuario superusuario. Las líneas de error y de información de la aplicación salen en esta terminal (es el equivalente local de `server.log`). Al terminar, `Ctrl+C` y no dejes el servidor corriendo.

Los fragmentos `js` se pegan en la consola del navegador (F12, pestaña Consola; si el navegador pide escribir `allow pasting`, hazlo).

1. **Aviso de error visible.** Abre `/base_datos/restaurar_bd/`. En la consola:
   ```js
   document.querySelectorAll('[required]').forEach(e => e.removeAttribute('required'));
   document.getElementById('form-restaurar').requestSubmit();
   ```
   No hay archivo, así que la vista responde antes de tocar la base: no se restaura nada. Debe aparecer arriba un aviso rojo «No se seleccionó ningún archivo.», legible, con el ícono, sin tapar el contenido.
2. **Mensajes que no se acumulan.** Registra un pago cualquiera (`/pagos/ingresar/`) y después abre `/base_datos/restaurar_bd/`: **no** debe aparecer la tarjeta verde «Base de Datos Restaurada Exitosamente». Tampoco debe verse ningún aviso de «Pago registrado» en la lista de pagos.
3. **Error de validación al crear un pedido.** En `/pedidos/nuevo/`: elige un cliente, agrega 2 productos, escribe un abono y elige el método **Transferencia**. En la consola: `document.querySelectorAll('[required]').forEach(e => e.removeAttribute('required'));`. Deja el resumen vacío y pulsa «Crear Pedido». Debe volver el formulario con el error junto al campo del resumen, los 2 ítems en la tabla, el abono y el método **Transferencia** elegido. Con una imagen de referencia elegida, además debe salir «Vuelve a elegir la imagen de referencia: el navegador no la conserva.»
4. **Error de validación al editar un pedido.** En un pedido de prueba: cambia el precio de un ítem, agrega otro, vacía el resumen (misma línea de consola) y guarda. Deben volver **tus** cambios (no los de la base). Sal sin guardar y confirma en el detalle que el pedido sigue igual.
5. **Lo mismo en cotizaciones:** `/cotizaciones/nueva/` y editar una cotización (con el resumen vacío).
6. **Ítem que no se puede guardar.** En `/pedidos/nuevo/`, con cliente y resumen válidos, en la consola:
   ```js
   document.getElementById('input-items-json').value = '[{"producto_id":"999999","cantidad":"1","precio_unitario":1000}]';
   document.getElementById('pedidoForm').requestSubmit();
   ```
   Debe volver el formulario (no la página 500) con «No pudimos guardar el detalle de productos. Lo que escribiste sigue en pantalla: revísalo y vuelve a guardar. Si el problema sigue, avisa en qué pantalla estabas y a qué hora.», sin pedido nuevo en la lista, y en la terminal **una** línea `ERROR` de `pedidos.views` con la traza, el método, la ruta y el usuario. Repite en editar pedido, crear cotización y editar cotización (el ítem de la base debe quedar igual).
7. **Envío repetido contra el servidor.** El navegador bloquea el doble clic, así que el servidor se prueba saltándose el navegador. En `/pedidos/nuevo/`, con un pedido completo, en la consola:
   ```js
   const f = document.getElementById('pedidoForm');
   const envio = () => fetch(location.href, {method: 'POST', body: new FormData(f), credentials: 'same-origin'});
   const r = await Promise.all([envio(), envio()]);
   console.log(r.map(x => x.status + ' ' + x.url));
   ```
   Las dos respuestas deben terminar en la **misma** página de detalle y en `/pedidos/lista/` debe haber **un solo** pedido nuevo. Repite en `/cotizaciones/nueva/` (`f` es el mismo `pedidoForm`) y en `/pagos/ingresar/` (cambia `getElementById('pedidoForm')` por `document.querySelector('form[data-bloquear-envio]')`): una cotización y un pago.
8. **Envío repetido por «atrás».** Guarda un pedido, vuelve con «atrás» a la página del formulario y pulsa guardar otra vez: debe llevarte al pedido ya creado, **sin** crear otro y sin mensaje.
9. **Formulario vencido.** En `/pedidos/nuevo/`, con un pedido completo, en la consola: `document.querySelector('[name=token_envio]').value = '';` y guarda. Debe volver el formulario con lo que escribiste y «Este formulario venció y no se guardó. Revisa los datos y vuelve a guardar.»; sin pedido nuevo. Guarda de nuevo: ahora sí se crea uno solo. En la terminal, una línea `INFO` «Envío sin token válido; no se guardó nada» (si tu configuración local muestra ese nivel).
10. **Botón bloqueado.** En DevTools, pestaña Red, elige «Slow 3G» para ver el estado. Pulsa dos veces seguidas el botón de: cliente nuevo, producto nuevo, cotización nueva, registrar pago, convertir cotización (en una cotización de prueba) y los cuatro «Eliminar» (con registros de prueba). El botón debe quedar deshabilitado con «Guardando…» («Convirtiendo…» y «Eliminando…» en esos dos) y salir **un** solo envío. Vuelve con «atrás»: el botón debe estar activo otra vez. En `/base_datos/restaurar_bd/` solo comprueba que «Cancelar» en la advertencia **no** deja el botón bloqueado; **no confirmes la restauración**. Vuelve la red a «Sin límite».
11. **Página 500.** Abre `/pagos/eliminar/<n.º de un pago>/` sin confirmar (la plantilla de confirmación no existe, AUD-02-002, y responde 500): debe verse «Si el problema sigue, avísale al administrador y cuéntale en qué pantalla estabas y a qué hora.», sin detalles técnicos, a 360 px también. En la terminal de `runserver` salen **dos** líneas de error: una de `django.request`, con la traza, el método, la ruta y el usuario, y otra de `django.server`, con el acceso (`500`). `django.server` existe solo en `runserver`: en PythonAnywhere queda únicamente la de `django.request`.
12. **Aviso y errores junto al campo.** En las pantallas de los pasos 3 a 5, revisa en claro y oscuro y a 360 px: el aviso rojo de arriba y los mensajes bajo cada campo se leen bien, no pulsan ni se animan, y con la tecla Tab el foco es visible. Si dispones de un lector de pantalla, al enfocar un campo con error debe leer su mensaje.

Instrucciones de lo que no puede hacer el agente (consultas a la réplica) no hacen falta: todo se comprueba en pantalla y en la terminal. No hay evidencia que pedir a producción: la medición de `access.log` sin pedidos duplicados es de la 03-05.

## Resultado de la ejecución (2026-11-04 y 2026-11-05)

Detalle, mediciones y desviaciones en [bitacora-03-04](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04.md).

- **Pasos 0 a 10** ejecutados en orden. Línea de partida: 220 pruebas, `OK (expected failures=9)`. **Final: 263 pruebas, `OK (expected failures=9)` en tres ejecuciones**; `check`: sin problemas; `makemigrations --check --dry-run`: `No changes detected`. R21 pasó por `expected failures=10` y volvió a 9.
- **Qué cambió en el código:** `views.py` (captura de `ERRORES_DE_ITEM` fuera del `atomic` en cuatro vistas, ítems y método de pago devueltos, token en tres vistas), `envio_unico.py` (nuevo), `forms.py` (`ErroresAccesiblesMixin`), `base.html` (bloque de mensajes de error), `index.js` (`bloquearBoton`, `desbloquearBoton`, `initBloqueoEnvio`), nueve plantillas con `data-bloquear-envio`, cinco con errores accesibles, `500.html` y `restaurar_bd.html`.
- **Pruebas:** archivos nuevos `test_contrato_error.py`, `test_envio_unico.py` y `test_bloqueo_envio.py`; R21 en `test_regresiones.py`; las pruebas de ítem fallido de `test_fronteras_transaccionales.py` y `test_pedidos.py` pasan de «500» a «formulario devuelto (200)»; los `ejecutar` de cinco módulos traen el token (`ayudas.con_token`).
- **Sin** migraciones, **sin** dependencias nuevas, **sin** tocar el precio del ítem, `DESIGN.md` ni el README.
- **Desviaciones:** (1) las pruebas de `test_envio_unico.py` y la de la línea `INFO` del rechazo se escribieron junto con el código, no antes (regla 15); la primera se verificó a posteriori apagando el token (18 de 19 fallan por la razón correcta, y se endurecieron seis que pasaban de forma trivial); (2) el aumento de consultas obligó a detenerse en el paso 4 (sección 11 de `AGENTS.md`); el desarrollador lo aceptó.

### Nota del 2026-11-06 · Corrección del abono (revisión de servidor)

La revisión de servidor ([bitacora-03-04-revision-servidor](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-revision-servidor.md)) encontró que, al devolver el formulario de crear pedido con error, el abono volvía vacío y el método de pago volvía marcado pero deshabilitado (no se enviaba). Corregido en `pedido_form.html` y `views.py` (`_abono_devuelto`), con cuatro pruebas nuevas en `FormulariosConservanLoEscritoTests`: **267 pruebas, `OK (expected failures=9)`**. Detalle en [bitacora-03-04-correccion-abono](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-correccion-abono.md). El estado de la iteración sigue «En revisión»: faltan los pasos [Visual] y la revisión manual del desarrollador. El segundo hallazgo de esa revisión (confirmación pendiente en `restaurar_bd`) quedó registrado como AUD-05-004, sin corregir.

### Nota del 2026-11-06 · Cierre

El desarrollador hizo la revisión manual el 2026-11-06 (dato dicho por él, no verificado por el agente): pasos 1 a 6 y 8 a 12 OK; el 7 lo cubrió la revisión de servidor. La iteración queda **Terminada**, con la excepción de la presentación del aviso rojo y del aviso de ítem fallido. Detalle en [bitacora-03-04-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-cierre.md).

- **Registrado para la Épica 08** (Auditoría 05, todos Baja y Abierto): AUD-05-005 (la cantidad del ítem parte en 0 y no se borra al escribir; el código declara `value="1"`, falta reproducirlo), AUD-05-006 (ícono y texto del aviso rojo desalineados), AUD-05-007 (el aviso de ítem fallido es un párrafo sin estructura; mismas palabras, solo presentación, y hay que ajustar las pruebas que comparan el HTML) y AUD-05-008 (`animate-pulse` y `text-red-500` en tres plantillas e importación de `settings` en `views.py`).
- **Decisión del desarrollador, sin hallazgo:** se deja el aviso nativo del navegador «Completa este campo».
- **Desviación 1 de la regla 15, cerrada:** con el token apagado (`envio_unico.estado` devuelve siempre «nuevo») fallan la prueba de la línea `INFO` del rechazo y R21 (`2 != 1`); con el código restaurado, en verde. Código idéntico (mismo SHA-256 y `git diff` vacío).
- **`despliegue.md`, sección 3.9:** la línea `INFO` del formulario vencido queda «por verificar en producción (03-05)».
- **Paso 11:** en `runserver` salen dos líneas de error (`django.request` con la traza y `django.server` con el acceso); en producción, una.
- **«Resuelto en 03-04»:** solo AUD-04-001 en su parte de servidor, con pruebas verdes (267, `OK (expected failures=9)`); el hallazgo sigue Abierto.
- **Propuesta para la Épica 08 (no se implementa):** candado de precio del ítem, en `registro-pendientes.md`, sección 4. El precio del ítem no se toca (`pruebas.md`, sección 9).

## Fuera de alcance

- Validación y despliegue con vigilancia intensiva, y la lectura de `access.log` para duplicados: 03-05.
- Hacer que los mutadores acepten solo POST (cambiar estado, duplicar, respaldo), la plantilla de eliminar pago (R7) y `duplicar_pedido` con `creado_por` (R19): 04-01.
- Respaldo y restauración (excepción propia de `utils.py`, `.sql` vacío): 04-04.
- Mostrar las confirmaciones de éxito, si la decisión 2 es A: queda como propuesta.
- Mensajes de los endpoints JSON de creación rápida (`index.js:254`, `:686`, JSON crudo): propuesta en `registro-pendientes.md`, sección 4. Cambiarlo toca el contrato con `index.js` (`AGENTS.md`, sección 9).
- La página 403 de CSRF y la sesión vencida: propuesta en la sección 4.
- Validar o recalcular el precio del ítem: **prohibido** (`pruebas.md`, sección 9).
- Fechas en UTC (R8, R9): 06-01. Mover la validación de ítems y las transacciones a servicios: 07-02.
- Imágenes de referencia huérfanas: decidido en la 03-03 (2-A).
- Los 13 errores de plantilla de AUD-02-021: sin causa conocida.

## Despliegue

- Cambia código, plantillas y JavaScript, así que necesita despliegue con etiqueta (RDA-007). **Viaja con la 03-05**, junto con la 03-01, la 03-02 y la 03-03. Sin migraciones con la decisión 5-A.
- Respaldo previo: lo decide el desarrollador en la 03-05. Con la 5-B o 5-C hay migración Clase 2 y el respaldo y el ensayo en la réplica son obligatorios.
- Los formularios abiertos al momento del despliegue no traen token (decisión 7): avisar o elegir una hora de poco uso.
- Retroceso: volver a la etiqueta anterior (`docs/operacion/retroceso.md`). Con la 5-A, sin migraciones que deshacer.

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| El token en la sesión suma consultas por página | Paso 0 y medición final; `AGENTS.md`, sección 11: si aumentan, consultar |
| Tocar `base.html` altera todas las pantallas | Revisión a 360 px en claro y oscuro; solo tokens de `DESIGN.md`; prueba de que `restaurar_bd` no duplica la tarjeta |
| Hacer visibles mensajes que nunca se vieron cambia lo que ve el usuario | Decisión 2 (A recomendada: solo errores) |
| Un token estricto rompe formularios abiertos durante el despliegue o muchas pruebas | Decisión 7; con la 4-A el usuario no pierde lo escrito; adaptar las pruebas en el paso 4 |
| Un aviso amable oculta un error real | La captura nueva registra con `logger.exception`; el mensaje no es el registro |
| Reescribir en el HTML el JSON del POST | Autoescape de Django y prueba con comillas y `<` (paso 3) |
| Tocar la corrección de la 00-07 antes de su medición del 2026-11-11 | Decisión 8 (C recomendada: `pedido_form.html` queda igual) |
| Mezclar propósitos con la 04-01 (POST), la 04-04 (respaldo) o la 07-02 (servicios) | «Fuera de alcance» y las decisiones 2, 3 y 10 fijan el límite |
| Los textos de error con `text-red-500` no cumplen AA y `animate-pulse` no está permitido | Paso 7 (patrón de la conversión de la 03-03). Se confirma al aprobar la redacción: es ajuste de plantillas que esta iteración ya toca, pero `DESIGN.md` deja sin definir estos puntos |
| La iteración es grande | Pasos ordenados con verificación propia; decisión 10 |
| Se pierde el formulario por un 500 inesperado aun con las decisiones 3 y 4 | Límite conocido: solo la opción 4-B lo cubre; la 4-A cubre los fallos que el servidor puede devolver |

## Decisiones del desarrollador

Todas resueltas el 2026-11-04, con la opción recomendada (en la 3, la B con respuesta 200; en la 8, la C):

1. **Mensajes de Django:** bloque común en `base.html`.
2. **Avisos que no son de error:** se muestran solo los de error; los demás se recorren y se descartan.
3. **Ítem que no se puede guardar:** capturar `ERRORES_DE_ITEM` fuera del `atomic`, registrar y devolver el formulario con los ítems, **con respuesta 200**.
4. **Qué se conserva:** `items_json` y `metodo_pago` del envío, y el aviso de la imagen.
5. **Token de envío único:** en la sesión, sin tabla ni migración.
6. **Envío repetido:** redirigir al registro ya creado, sin mensaje.
7. **POST sin token válido:** rechazar y devolver el formulario con los datos y un token nuevo.
8. **Bloqueo del botón:** función común en `index.js`; `pedido_form.html` conserva el script de la 00-07.
9. **Texto de la restauración fallida:** sin la mención de `backups/`.
10. **Una sola iteración.**

**Paso 7 aprobado:** `text-red-600`, `role="alert"`, `aria-invalid`, `aria-describedby` y sin `animate-pulse`, solo en las plantillas que la iteración ya toca.

**Textos aprobados** (ver la sección «Textos aprobados»).

**Costo de consultas aceptado (2026-11-04), al detenerse en el paso 4 por la sección 11 de `AGENTS.md`.** La 5-A sigue tal como está: el token en la sesión suma **+3 consultas por cada GET y cada POST exitoso** de crear pedido, crear cotización e ingresar pago (+1 real, sin `BEGIN` y `COMMIT`: el guardado de la sesión es `BEGIN`, `UPDATE`, `COMMIT`). El **tope de 20 tokens** queda confirmado. Medición (mismo método que [bitacora-03-03-medicion]({B}bitacora-03-03-medicion.md); detalle en [bitacora-03-04]({B}bitacora-03-04.md)):

| Petición | Antes | Después | Sin `BEGIN` y `COMMIT` antes → después |
| :------- | ----: | ------: | :------------------------------------- |
| GET `crear_pedido` | 4 | 7 (+3) | 4 → 5 |
| POST `crear_pedido` | 16 | 19 (+3) | 14 → 15 |
| GET `crear_cotizacion` | 4 | 7 (+3) | 4 → 5 |
| POST `crear_cotizacion` | 11 | 14 (+3) | 9 → 10 |
| GET `ingresar_pago` | 6 | 9 (+3) | 6 → 7 |
| POST `ingresar_pago` | 13 | 16 (+3) | 11 → 12 |
| GET `lista_pagos` (con el bloque de mensajes) | 4 | 4 | — |
| GET `editar_pedido` | 6 | 6 | — |

**Verificación a posteriori de `test_envio_unico.py` (2026-11-04), desviación de la regla 15 corregida:** las pruebas del token se escribieron junto con la implementación. Se desactivó temporalmente el token en las tres vistas, se corrieron y se restauró el código (idéntico byte a byte y por `git diff`). Resultado en la bitácora.

Estado de la iteración: se usa «Pendiente (redactada)» mientras no se ejecuta (el README protegido no define «Redactada»).

## Datos requeridos del cliente

- Ninguno nuevo para redactar la iteración.
- Si la decisión 3 es C: qué ítems se consideran válidos (por ejemplo cantidad 0 o negativa) es regla de negocio `PENDIENTE_CLIENTE`.
- Siguen abiertos, sin cambiar de comportamiento aquí: valor de una cotización neto o con IVA (AUD-02-014), pedido de $0 como pagado y sobrepago (`registro-pendientes.md`, sección 2).
