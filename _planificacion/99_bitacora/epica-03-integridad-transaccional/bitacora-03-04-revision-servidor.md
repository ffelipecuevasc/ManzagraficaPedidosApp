# Bitácora 03-04 · Revisión de servidor

- **Fecha:** 2026-11-06
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la 03-04 sigue En revisión: faltan los pasos [Visual] del desarrollador y la decisión sobre los dos hallazgos de abajo). Solo mediciones y este documento; sin cambios en código, plantillas ni pruebas.

## Resumen

Se ejecutó la parte de servidor de la sección «Revisión manual» de [iteracion-03-04](../../10_epicas/epica-03-integridad-transaccional/iteracion-03-04-contrato-de-error-hacia-el-usuario.md) contra la réplica local (`manzagrafica_replica`), con `DEBUG=False`, un servidor de un solo hilo y formularios reales enviados por HTTP con cookie de sesión y token CSRF. De los 12 pasos, 10 tienen una parte que se verifica con HTTP, base y registro; los pasos 10 y 12 son solo [Visual] y no se ejecutaron. Complementa [bitacora-03-04](bitacora-03-04.md), que no se edita (regla 5.4).

Resultado: **29 de 32 comprobaciones en verde**. Las 3 en rojo son: un hallazgo real (el abono no vuelve al formulario), un hallazgo real de alcance acotado (una confirmación de éxito pendiente se pinta en `restaurar_bd`) y una expectativa mía mal planteada (`restaurar_bd` no usa el atributo `data-bloquear-envio` por diseño). Nada se corrigió.

## Método

- **Servidor:** `python manage.py runserver --insecure --nothreading --noreload` con `DB_NAME=manzagrafica_replica` y `DEBUG=False`, salida a un archivo temporal. Dos diferencias con la preparación del documento: se agregó `--noreload` (el recargador crea un proceso hijo difícil de detener) y `PYTHONUTF8=1` (la salida va a un archivo, no a la consola, y el formato del registro antepone emojis). Se comprobó antes que la base activa era `manzagrafica_replica`.
- **Cliente:** un script temporal **fuera del repositorio** (carpeta temporal de la sesión). Creó la sesión del usuario 1 con `SessionStore` y las claves de autenticación de Django, **sin** llamar a `login()`, para no actualizar `last_login` de un usuario existente. Envió los formularios con `http.client`, la cookie de sesión y el token CSRF en la cabecera `X-CSRFToken`.
- **Datos de prueba:** un cliente y dos productos creados por el ORM (`PRUEBA-0304`), y el resto (pedidos, cotizaciones, pagos) por los propios formularios de la aplicación. Ningún dato existente se modificó ni se borró. No se imprimieron nombres, teléfonos ni correos de clientes, ni `.env` ni `SECRET_KEY`.
- **Conteos y registro:** antes y después de cada envío se contaron pedidos, ítems de pedido, pagos, cotizaciones, ítems de cotización y eventos de auditoría (solo lectura), y se leyeron las líneas nuevas del registro del servidor (nivel, registrador, método, ruta, usuario, traza).
- **Doble envío:** dos hilos con barrera, dos conexiones simultáneas, mismo token y mismo cuerpo.
- **Restauración:** solo se envió el formulario **sin archivo**. No se ejecutó respaldo ni restauración.
- **Cierre:** servidor detenido (puerto 8000 sin escucha), script, archivo de salida y resultados borrados, y las dos sesiones creadas por el script borradas. `Session` volvió a 104 filas, igual que al comenzar.

## Resultado por paso

Tipo: **[Servidor]** se comprobó aquí; **[Visual]** no se ejecutó. «+ [Visual]» indica que el paso tiene además una parte que solo se ve en el navegador (esa parte queda en la lista de pendientes del desarrollador).

| Paso | Tipo | Resultado esperado | Resultado obtenido | Evidencia |
| :--: | :--- | :----------------- | :----------------- | :-------- |
| 1 | [Servidor] + [Visual] | `POST` sin archivo a `restaurar_bd` → 302 de vuelta; el HTML trae el aviso rojo «No se seleccionó ningún archivo.» con `role="alert"` e ícono; nada restaurado | **Cumple.** 302 a `/base_datos/restaurar_bd/`; aviso presente con `role="alert"` y `error_outline`; sin tarjeta de éxito; una segunda carga ya no lo trae (se consumió); conteos sin cambios; 0 líneas `ERROR` | HTML de la pantalla y conteos |
| 2a | [Servidor] | Pago → lista de pagos → `restaurar_bd`: ni «Pago registrado» en la lista ni tarjeta verde | **Cumple.** 302 a `/pagos/lista/`; «registrado correctamente» ausente; sin alerta roja; «Restaurada Exitosamente» y «Pago de $» ausentes en `restaurar_bd` | Pago 1066 |
| 2b | [Servidor] (variante mía) | Pago → `restaurar_bd` **sin** pasar por la lista: sin tarjeta verde | **No cumple.** Con el 302 sin seguir, la siguiente pantalla `restaurar_bd` pinta la tarjeta «¡Base de Datos Restaurada Exitosamente!» con el texto «Pago de $700…». Ver contradicción 2 | Pago 1067 |
| 3 | [Servidor] + [Visual] | Resumen vacío, 2 ítems, abono y Transferencia → 200, error junto al campo, ítems, abono y método conservados, token vigente, nada escrito | **Cumple en todo salvo el abono.** 200; `error-resumen_pedido` con `role="alert"`, `aria-invalid` y `aria-describedby`; `items_json` devuelto idéntico (con `<`, `"` y `&` escapados); `Transferencia` marcada; mismo token; conteos sin cambios; 1 línea `INFO` de formulario inválido solo con nombres de campo. **El campo del abono vuelve vacío y el `<select>` del método vuelve `disabled`.** Ver contradicción 1 | HTML: `<input … name="abono_inicial" … placeholder="0" min="0">` sin `value` |
| 3 (imagen) | [Servidor] | Con imagen de referencia, además el aviso «Vuelve a elegir la imagen de referencia: el navegador no la conserva.» | **Cumple.** 200, aviso presente, ítems conservados, nada escrito, `media/referencias` con 0 archivos antes y después | PNG de 1×1 píxel |
| 3 (corregir) | [Servidor] | Guardar el pedido corregido crea uno solo | **Cumple.** 302 al detalle | Pedido 914 |
| 4 | [Servidor] + [Visual] | Editar pedido con resumen vacío: vuelven los ítems **del usuario**, no los de la base; la base queda igual | **Cumple.** 200; `items_json` igual al enviado (3 ítems con precio cambiado); error junto al campo; ítems, valor y resumen de la base iguales; conteos sin cambios | Pedido 915 |
| 5 | [Servidor] + [Visual] | Lo mismo en cotizaciones (crear y editar) | **Cumple.** Crear: 200, ítems devueltos, error junto al campo, mismo token, nada escrito. Editar: 200, ítems del usuario, base igual | Cotización 31 |
| 6 | [Servidor] + [Visual] | Ítem que no se puede guardar, en las 4 vistas y las 5 causas: 200 con el aviso fijo, una línea `ERROR` de `pedidos.views` con traza, método, ruta y usuario, nada escrito, ítems de la base iguales, sin página 500 | **Cumple las 20 combinaciones** (crear y editar pedido; crear y editar cotización; producto inexistente, JSON inválido, clave ausente, cantidad no numérica y precio no numérico). Cada una: 200, texto aprobado literal, exactamente 1 línea `ERROR` con traza, `metodo=POST`, ruta correcta y `usuario=1`, 0 líneas `django.request`, conteos sin cambios; en «crear» el token vuelve vigente; en «editar» ítems, valor y resumen idénticos. Total en el registro: 20 `ERROR` de `pedidos.views` | Línea de ejemplo: `🔴 nivel=ERROR registrador=pedidos.views metodo=POST ruta=/pedido/editar/915/ usuario=1 excepcion=ValueError mensaje="Un ítem del pedido no se pudo guardar al editar"` |
| 7 | [Servidor] | Dos POST simultáneos con el mismo token terminan en el mismo destino y crean un solo registro | **Cumple en las tres.** Pedido: 302 y 302 a `/921/`; +1 pedido, +2 ítems, +1 pago (el abono), +1 evento. Cotización: 302 y 302 a `/cotizaciones/detalle/37/`; +1 cotización, +2 ítems. Pago: 302 y 302 a `/pagos/lista/`; +1 pago, +1 evento. 0 líneas `ERROR` en el pedido | Pedido 921, cotización 37, pago 1069 |
| 8 | [Servidor] + [Visual] | Reenvío del mismo formulario (lo que hace «atrás» y guardar) lleva al registro ya creado, sin crear otro y sin mensaje | **Cumple** (pedido y cotización). 302 y 302 al mismo destino; +1 pedido en total; sin alerta en el detalle. El «atrás» del navegador no se probó | Pedido 922, cotización 38 |
| 9 | [Servidor] | Token vacío → formulario devuelto con lo escrito y «Este formulario venció y no se guardó. Revisa los datos y vuelve a guardar.», token nuevo, nada creado, una línea `INFO`; guardar de nuevo crea uno solo | **Cumple en pedido, cotización y pago.** 200, aviso literal, datos conservados, token nuevo, conteos sin cambios, exactamente 1 línea `INFO` «Envío sin token válido; no se guardó nada» con `POST`, ruta y `usuario=1`. Con el token nuevo: 302 y +1 registro | Línea de ejemplo: `🔵 nivel=INFO registrador=pedidos.views metodo=POST ruta=/pedidos/nuevo/ usuario=1 excepcion=- mensaje="Envío sin token válido; no se guardó nada"`. Pedido 923, cotización 39, pago 1070 |
| 9 (extra) | [Servidor] | Campo ausente, token inventado y token de otro formulario (pago) se tratan igual | **Cumple.** Tres casos: 200, aviso, nada creado. Total de líneas `INFO` de rechazo en el registro: 7 (3 de token vacío, 3 de estos casos y 1 del tope) | — |
| 9 (extra) | [Servidor] | Tope de 20 tokens: el primero de 21 emitidos sin usar queda vencido | **Cumple.** 200, aviso, nada creado. El valor 20 sigue `PENDIENTE_DESARROLLADOR` (`envio_unico.py:17`: «a confirmar en la revisión manual») | — |
| 10 | [Visual] (complemento servidor) | Botón deshabilitado con «Guardando…», un solo envío, recuperación con «atrás», «Cancelar» de SweetAlert | **No ejecutado.** Complemento de servidor: las 9 pantallas con formulario común responden 200 con `data-bloquear-envio` (clientes y productos nuevos, cotización nueva, pago, convertir, y los cuatro «Eliminar»). `restaurar_bd` responde 200 **sin** el atributo, por diseño: bloquea con `bloquearBoton(…, 'Restaurando…')` después de la confirmación (decisión 8-C). No fue una falla | GET sin escribir |
| 11 | [Servidor] + [Visual] | `GET /pagos/eliminar/<n>/` (sin plantilla, AUD-02-002) → 500 con el texto de la 500, sin detalles técnicos, una línea `django.request` con la ruta | **Cumple.** 500; texto «Si el problema sigue, avísale al administrador y cuéntale en qué pantalla estabas y a qué hora.» presente; sin `Traceback`, `TemplateDoesNotExist`, rutas del servidor ni nombres de plantilla; 1 línea `django.request` con `ruta=/pagos/eliminar/1066/`, `usuario=1`, `excepcion=TemplateDoesNotExist` y traza; el pago sigue existiendo; conteos sin cambios. A 360 px no se vio. Ver nota 3 | Pago 1066 |
| 12 | [Visual] | Contraste, foco, 360 px, claro y oscuro, no pulsar ni animar, lector de pantalla | **No ejecutado.** Solo se comprobó en el HTML que cada error junto al campo trae `id="error-<campo>"`, `role="alert"` y el campo `aria-invalid` y `aria-describedby` (pasos 3 a 5) | — |

## Contradicciones sin corregir

1. **El abono no se conserva (paso 3).** La iteración dice que al fallar la validación «debe volver el formulario con […] el abono y el método **Transferencia** elegido», y su criterio de término habla de «los datos ingresados». En `pedido_form.html:386-392` (el `<input>` abre en la línea 386) el campo `abono_inicial` se escribe a mano, sin `value`: vuelve vacío. Como `index.js:779-804` deshabilita el `<select>` del método cuando el abono es 0 o está vacío, el método vuelve **marcado pero deshabilitado**; el usuario tiene que volver a escribir el abono para poder enviarlo (si no lo escribe, `metodo_pago` no se envía). Las pruebas automáticas no lo detectan: `FormulariosConservanLoEscritoTests` revisa ítems y método, no el abono (`test_contrato_error.py:127-135`). Esta rama no tiene corrección; decide el desarrollador.
2. **Una confirmación de éxito pendiente se pinta en `restaurar_bd` (variante 2b).** `base.html` descarta los mensajes que no son de error, pero `restaurar_bd.html:106-107` conserva su propio recorrido de `messages` y pinta cada `success` como la tarjeta de restauración. Si un `success` queda en la cola y la siguiente pantalla es `restaurar_bd` (por ejemplo, un `POST` de pago cuyo redireccionamiento no se sigue), aparece «¡Base de Datos Restaurada Exitosamente!» con el texto del pago. La prueba automática `test_un_pago_registrado_no_aparece_como_restauracion_exitosa` usa `follow=True`, que visita la lista de pagos y consume el mensaje antes; por eso no ve este camino. **Alcance:** el paso 2 tal como lo escribe el documento (pago, lista, `restaurar_bd`) sí cumple (2a). En el uso normal el redireccionamiento carga una pantalla con `base.html`, así que es difícil de alcanzar; queda como riesgo bajo. Decide el desarrollador si se cierra (por ejemplo, filtrando por nivel o eliminando el recorrido propio).

## Notas

1. **Huecos de numeración (esperado).** Los intentos que MySQL revirtió dejaron huecos de `AUTO_INCREMENT`: pedidos 916 a 920 y cotizaciones 32 a 36 (las cinco causas del ítem fallido en «crear»). No hay filas sueltas: los conteos de pedidos, ítems, pagos y cotizaciones no variaron en ningún intento fallido.
2. **Registro local.** Las líneas de acceso de `runserver` no salen en la terminal (la configuración de `LOGGING` solo muestra, de `django.server`, las respuestas de nivel `ERROR`): el único acceso visible es el 500 del paso 11. El archivo no tuvo ningún `Logging error` por los emojis. El registro final tuvo 20 `ERROR` de `pedidos.views`, 1 de `django.request` y 1 de `django.server` (el acceso del 500), 21 trazas y 7 `INFO` de rechazo de token.
3. **Paso 11, dos líneas de error.** Además de la línea `django.request` que describe el documento, el 500 deja una línea `django.server` de nivel `ERROR` con el acceso (`"GET /pagos/eliminar/1066/ HTTP/1.1" 500`). El documento dice «una línea `django.request`»: se cumple, pero en la terminal salen dos. Ninguna lleva datos de clientes.
4. **La traza de la 500 lleva rutas del servidor** (`D:\…\site-packages\…`) en el registro, no en la respuesta: es lo esperado (la traza es para el administrador).
5. **El token por sesión** tiene tope de 20 y se comprobó que el 21.º lo descarta. El valor sigue sin confirmarse (`PENDIENTE_DESARROLLADOR`).

## Pasos que quedan [Visual] para el desarrollador

Pasos 10 y 12 completos, y la parte visual de los pasos 1, 3, 4, 5, 6, 8, 9 y 11. Instrucciones breves en el resumen entregado al desarrollador (preparación con PowerShell 7 del documento de la iteración, sección «Revisión manual»).

## Datos de prueba creados (para limpiar al refrescar la réplica, AUD-05-002)

Todo lo creado lleva «PRUEBA-0304» en el nombre, el resumen o la nota. IDs:

| Tabla | IDs | Conteo antes → después |
| :---- | :-- | :--------------------- |
| `Cliente` | 743 | 736 → 737 |
| `Producto` | 59 y 60 | 55 → 57 |
| `Pedido` | 914 (A), 915 (B), 921 (doble envío), 922 («atrás»), 923 (paso 9) | 891 → 896 |
| `ItemPedido` | los 10 de esos cinco pedidos (2 cada uno) | 875 → 885 |
| `Pago` | 1066, 1067, 1068 (abono inicial del pedido 921), 1069, 1070 | 1056 → 1061 |
| `Cotizacion` | 31 (C), 37 (doble envío), 38 («atrás»), 39 (paso 9) | 28 → 32 |
| `ItemCotizacion` | los 8 de esas cuatro cotizaciones (2 cada una) | 57 → 65 |
| `RegistroEvento` | 14 a 22 (`pedido_creado` ×5, `pago_registrado` ×4) | 13 → 22 |
| `Session` | ninguna: las dos sesiones del script se borraron | 104 → 104 |

El pedido 915 y la cotización 31 quedaron como se crearon (los intentos de edición con error no los cambiaron). Ningún pedido, pago ni cotización existente se tocó.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-revision-servidor.md` | Nuevo (este documento) |

Archivos temporales (borrados, fuera del repositorio): el script de revisión, un segundo script para confirmar el abono, la salida del servidor y los resultados.

## Verificación

- Base activa: `manzagrafica_replica` (comprobada antes de crear datos). `DEBUG=False`.
- Revisión de servidor: 29 de 32 comprobaciones en verde; las 3 restantes explicadas arriba.
- No se ejecutó la suite de pruebas ni se tocó código: no hay cambios que verificar con ella.
- `git status --short` al terminar: solo este documento nuevo.

## Migraciones

- Ninguna.

## Commit sugerido

`Épica 3 - Iteración 03-04: revisión de servidor (pasos 1 a 9 y 11); el abono no vuelve al formulario y un éxito pendiente se pinta en restaurar_bd`
