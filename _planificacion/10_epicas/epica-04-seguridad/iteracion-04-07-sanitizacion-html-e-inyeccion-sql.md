# Iteración 04-07 · Sanitización del HTML enriquecido y revisión de inyección SQL

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-07-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-07-redaccion.md)); D1 a D4 resueltas por el desarrollador el mismo día ([bitacora-04-07-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-07-cierre.md)).
- **Subfase del plan:** nueva (Auditoría 03); `definicion-epica-04.md`, alcance 7 y decisión de la épica sobre la 04-07.
- **Depende de:** nada técnico de las anteriores; comparte `pedido_detail.html` con la 04-01 (otras líneas) y `forms.py` con la 04-08, y se desarrolla sobre lo que dejen. No toca `views.py`. Se redactó en paralelo a la vigilancia de la 03-05; **su ejecución en local no empieza hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17). **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-10 → 04-02 → 04-03 → 04-04 → 04-05 → 04-06 → **04-07**.
- **Es requisito de:** la Épica 09 (operadores, RDA-017) y la 08-07 (registro, sección 1).
- **RDA relacionadas:** RDA-007; RDA-017 (exige la sanitización antes de los operadores); **RDA-020: propuesto; se escribe al ejecutar la 04-07** (D2; la última vigente es RDA-019; no se agrega a `decisiones.md` hasta entonces).
- **Hallazgos que cierra:** AUD-03-001.
- **Cambio de esquema:** ninguno. **Sin operación sobre datos** (D4): el HTML ya guardado se revisa en la réplica, pero no se limpia.
- **Respaldo previo al despliegue:** sí, el de rutina (no hay migración ni limpieza de datos).
- **Archivos que tocará la ejecución:** `requirements.txt` (dependencia `nh3`; la consulta previa está respondida, ver D2), `pedidos/sanitizar.py` (nuevo), `pedidos/templatetags/` (paquete nuevo con el filtro `html_seguro`; **no existe hoy**, verificado), `pedidos/forms.py` (`clean_<campo>` de `PedidoForm`, `CotizacionForm` y `ProductoForm`), las tres plantillas de detalle, pruebas nuevas y `decisiones.md` (RDA-020, al ejecutar).

## Objetivo

Que el HTML que se escribe en el editor enriquecido solo pueda contener las etiquetas de formato que el editor ofrece, que nada de lo guardado ejecute JavaScript al mostrarse, y que quede documentado (y vigilado) que la aplicación no arma SQL con texto.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main`, con archivo y línea.
- **Inferido:** sale de leer el código o la documentación; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## El problema: XSS almacenado

Django escapa todo lo que imprime una plantilla: un `<` se convierte en `&lt;` y el navegador lo muestra como texto. El filtro `|safe` apaga esa protección y le dice a Django «este texto ya es HTML confiable, imprímelo tal cual». Si el texto viene de un formulario, cualquiera que escriba en ese campo decide qué HTML recibe el navegador de quien lo abre.

Ejemplo (**no es código del proyecto**, solo ilustra el ataque): alguien guarda como detalle de un pedido

```html
<p>Polera talla M</p><img src="x" onerror="fetch('/usuarios/...', {method:'POST'})">
```

La imagen no existe, el navegador ejecuta `onerror` y ese JavaScript corre **con la sesión de quien abrió el detalle**: puede hacer cualquier cosa que esa persona pueda hacer (leer datos, enviar formularios con su token CSRF, que está en la misma página). Se llama «almacenado» porque el ataque queda guardado en la base y se dispara cada vez que alguien abre la pantalla.

**Por qué es requisito de la Épica 09:** hoy solo escribe un superusuario, que ya puede hacerlo todo; atacarse a sí mismo no le da nada nuevo. La Épica 09 agrega **operadores** (RDA-017), que no tienen acceso al módulo de base de datos ni a usuarios. Un operador que escriba ese HTML en un pedido haría que el **superusuario**, al abrirlo, ejecute acciones de superusuario sin saberlo. Por eso AUD-03-001 pasa a Alta antes de la 09, y RDA-017 pide esta iteración primero.

## Qué hay hoy (verificado)

### Usos de `|safe`, `mark_safe` y similares (búsqueda en `pedidos/` y `PedidosApp/`)

| Archivo y línea | Uso | Origen del dato |
| :-------------- | :-- | :-------------- |
| `pedido_detail.html:115` | `{{ pedido.detalles_pedido\|safe\|default:"…" }}` | Usuario (Summernote) |
| `cotizacion_detail.html:150` | `{{ cotizacion.detalles\|safe }}` | Usuario (Summernote) |
| `producto_detail.html:53` | `{{ producto.descripcion\|safe }}` | Usuario (Summernote), **también** por la creación rápida `api_crear_producto_rapido` (`views.py:1147`, usa `ProductoForm`) |

- **`mark_safe`, `format_html`, `SafeString`, `{% autoescape off %}`:** ninguno en código de aplicación. `test_contrato_error.py:126` comprueba que el autoescape protege un mensaje.
- **Otros lugares donde se muestran esos campos, ya seguros:** `cotizacion_pdf.html:289` y `:318` y `producto_list.html:77` usan `|striptags` sin `|safe`, así que el resultado se escapa (inferido del comportamiento de Django; el PDF se genera con WeasyPrint, que no ejecuta JavaScript).
- **Otra vía de escritura:** el admin de Django registra `Pedido` y `Producto` (`admin.py:11`, `:19`); quien entra al admin ya es `is_staff`. Sus campos son cuadros de texto que Django escapa, pero **lo que se guarda por ahí no pasa por los formularios de la aplicación**: lo cubre el filtro al mostrar (D1).
- **Otras vías que copian texto sin formulario:** `duplicar_pedido` copia `detalles_pedido` (`views.py:490`) y la conversión de cotización a pedido copia `cotizacion.detalles` a `detalles_pedido` (`views.py:982`): ambas heredan lo guardado sin pasar por un formulario, y las cubre el filtro al mostrar.

### El editor (Summernote)

- Summernote `0.8.18` desde CDN (`base.html:38` y `:327`); se activa en los tres campos (`pedido_form.html:347`, `cotizacion_form.html:292`, `producto_form.html:96`, y `forms.py:134`).
- Barra de herramientas (`index.js:94-102`): **negrita, cursiva, limpiar formato, lista con viñetas y lista numerada**. Imágenes bloqueadas (`onImageUpload`, `disableDragAndDrop`) y pegado reducido a texto plano (`onPaste`).
- **Etiquetas que produce el editor (inferido de esa barra y del comportamiento de Summernote; se confirma en la réplica):** `p`, `br`, `b`, `strong`, `i`, `em`, `ul`, `ol`, `li`, y posiblemente `span` con `style` al limpiar formato, o `div` en la primera línea. **Todo esto lo hace el navegador:** quien envía el formulario sin el editor (o con las herramientas del navegador) puede mandar cualquier HTML. La defensa tiene que estar en el servidor.

### Modelos

- `Pedido.detalles_pedido` (`models.py:41`) y `Producto.descripcion` (`:120`): `TextField` con nulo; `Cotizacion.detalles` (`:166`): `TextField` obligatorio.

### Inyección SQL

- **Única consulta SQL directa de la aplicación:** `utils.py:155-162`, `SELECT SUM(data_length + index_length) FROM information_schema.TABLES WHERE table_schema = %s`, ejecutada con `cursor.execute(sql, [db_name])`: **parametrizada**, y el valor viene de `settings`, no del usuario.
- `test_entorno.py:10-12` ejecuta SQL fijo (pruebas, sin datos del usuario).
- **Ninguno** de `.raw(`, `.extra(`, `RawSQL` en `pedidos/` (búsqueda). El resto pasa por el ORM, que siempre parametriza.
- `restaurar_bd_mysql` pasa un archivo a `mysql` (`utils.py:121-126`): no es SQL armado con texto, es la restauración (04-04).

### Dependencias

`requirements.txt` no tiene ningún sanitizador (ni `nh3` ni `bleach`). Django no trae uno.

## Contradicciones con la planificación

- **La definición dice «revisar en la réplica el HTML ya guardado en producción».** La réplica es una copia de producción a la fecha de su último refresco; la revisión vale para esa fecha, y lo escrito después solo se ve en producción (no verificado).
- **Summernote viene de un CDN** (contra `AGENTS.md`, regla 8.17, «no se agregan recursos nuevos»; no es nuevo). Lo resuelve la 08-07, que depende de esta iteración; aquí no se toca.
- **`|safe|default`** en `pedido_detail.html:115`: el orden no es un problema de seguridad, pero al sanitizar se revisa que un detalle vacío tras limpiar siga mostrando el texto por defecto.
- **El filtro propio necesita un paquete que no existe** (`pedidos/templatetags/`): la redacción inicial lo daba por supuesto; se agrega a los archivos de la ejecución.

## Alcance

1. **Lista blanca** de etiquetas, sin atributos (D3), para `pedido.detalles_pedido`, `cotizacion.detalles` y `producto.descripcion`, aplicada **al guardar y al mostrar** (D1), en una sola función (`pedidos/sanitizar.py`) basada en `nh3` (D2).
2. **Al guardar:** `clean_<campo>` en `PedidoForm`, `CotizacionForm` y `ProductoForm`, que también cubre la creación rápida de productos (`api_crear_producto_rapido`).
3. **Al mostrar:** filtro propio `html_seguro` (paquete `pedidos/templatetags/`) que sanitiza y marca el resultado como seguro; reemplaza a `|safe` en las tres plantillas y protege lo ya guardado, lo del admin y lo que copian la duplicación y la conversión.
4. **Revisión de inyección SQL documentada** (sección anterior) y una **prueba-guardia** con el módulo `ast` (D4) que recorre `pedidos/*.py` (sin pruebas ni migraciones) y falla si encuentra `.raw(`, `.extra(`, `RawSQL(` o un `execute(` cuyo primer argumento sea un f-string, una concatenación o `%`/`.format`.
5. **Revisión del HTML ya guardado en la réplica** (solo lectura, solo conteos, sin copiar contenidos): cuántos registros de cada campo traen etiquetas o atributos fuera de la lista blanca. **No se limpia nada** (D4): si hay contenido peligroso, se anota el conteo y se propone una limpieza aparte, con respaldo previo, como operación sobre datos. **El agente no ejecuta nada contra la base**: entrega la consulta (anexo) y la corre el desarrollador.
6. **Registrar RDA-020 al ejecutar** (propuesto: «Sanitización del HTML enriquecido con `nh3`, al guardar y al mostrar»).
7. **Fuera:** limpiar datos ya guardados (D4); sacar Summernote del CDN (08-07); política de contenido (04-09); otros campos de texto sin `|safe` (ya escapados); ampliar la lista blanca (si la revisión de la réplica muestra que hace falta, se detiene y se consulta).

## Decisiones (resueltas por el desarrollador, 2026-11-17)

| # | Decisión | Resuelta como |
| :- | :------- | :------------ |
| D1 | Cuándo sanitizar | **Al guardar y al mostrar** (opción A). |
| D2 | Con qué herramienta | **`nh3`** (opción A), con RDA-020. La **consulta previa** que exige `AGENTS.md` (secciones 6 y 11) para la dependencia nueva **está respondida** (autorizada por el desarrollador, dicho por él). **RDA-020: propuesto; se escribe al ejecutar la 04-07.** El paso 0 conserva la comprobación de instalación en PythonAnywhere (Python 3.13). |
| D3 | Qué permite la lista blanca | **Exactamente lo que ofrece la barra actual** (negrita, cursiva, limpiar formato y listas): `p`, `br`, `b`, `strong`, `i`, `em`, `ul`, `ol`, `li`, **sin atributos** (ni `style`, ni `class`, ni `href`). Comentarios y etiquetas desconocidas se eliminan conservando su texto; `script` y `style` se eliminan con su contenido. |
| D4 | Datos ya guardados y forma de la guardia | **No se limpian** datos ya guardados en esta iteración (se revisan en la réplica; el filtro al mostrar ya los neutraliza). Prueba-guardia de SQL con `ast`, sin dependencias. |

**Qué se descartó (para no volver a discutirlo):** `bleach` (obsoleto según sus autores, inferido de su anuncio; no revisado), sanitizador propio con `html.parser` (donde nacen los errores de seguridad) y texto plano (cambia lo que ve el usuario).

**Justificación de la dependencia que pide `AGENTS.md`, sección 6** (peso y disco se miden en la ejecución, no están medidos): *peso y disco:* `pip download nh3==<versión>` en local y `du` antes y después en el servidor, anotados en la bitácora; *arranque en frío:* se importa dentro de la función que sanitiza (regla 8.9), no al arrancar; *alternativa sin dependencia:* el sanitizador propio, descartado por D2.

## Pasos

0. **Comprobación de instalación en PythonAnywhere (Python 3.13), la hace el desarrollador, antes de seguir.** En una consola del servidor, en el entorno virtual de la web app (no verificado cuál usa), instalar la versión exacta de `nh3` y comprobar que importa y que `nh3.clean('<p>a</p><script>b</script>', tags={'p'})` devuelve `<p>a</p>`. Anotar versión, peso en disco y segundos de CPU gastados (el plan gratuito da 100 s diarios a consolas y tareas). **Inferido, no verificado:** `nh3` se distribuye como rueda precompilada para Linux, así que no debería compilar Rust, y PyPI está en la lista blanca de salida. **Si no instala, la iteración se detiene** y se vuelve a la D2 con el desarrollador (no se cae a otra opción por cuenta propia). Con eso queda cerrada la consulta previa en la práctica.
1. Respaldo de la réplica. Línea base: `test pedidos` (número y fallos esperados tras la 04-06).
2. **Revisión en la réplica** (la ejecuta el desarrollador con la consulta del anexo): conteo de registros por campo con `<script`, eventos `on…=`, `javascript:`, `<iframe`, `<img`, `<svg`, `<style`, `style=`, `class=`, `<a `, `<div`, `<span`, `<table` y `data:`. Solo conteos en la bitácora, con la fecha del último refresco de la réplica.
3. Pruebas primero (tabla siguiente); ver fallar las de `<script>` y atributos.
4. `requirements.txt` con la versión exacta (UTF-8 sin BOM y LF, regla 8.16), `pedidos/sanitizar.py`, `clean_*` en los tres formularios, paquete `pedidos/templatetags/` con `html_seguro` y las tres plantillas.
5. Prueba-guardia de SQL.
6. Revisión manual en la réplica: crear y editar un pedido, una cotización y un producto con negrita, cursiva y listas; ver los detalles y el PDF; escritorio y 360 px.
7. Bitácora, registro, auditoría (AUD-03-001), **RDA-020 en `decisiones.md` (se escribe ahora)**, estado «En revisión».

## Pruebas

| Punto | Prueba |
| :---- | :----- |
| `<script>` no se ejecuta | Un pedido guardado **directo en la base** (sin formulario) con `<p>a</p><script>alert(1)</script>`: el HTML de `pedido_detail` no contiene `<script` ni `alert(1)` y sí `<p>a</p>`. Lo mismo para cotización y producto. |
| Variantes | `<SCRIPT>`, `<svg onload=…>`, `<iframe src=…>`, `<style>` y un comentario `<!-- -->`: ninguno llega a la respuesta. |
| Atributos (D3) | `<img src=x onerror=alert(1)>`, `<a href="javascript:…">x</a>` y `<p class="a" style="color:red">t</p>`: la respuesta no contiene `onerror`, `javascript:`, `class` ni `style`; el texto `x` y `t` se conserva (sin la etiqueta o como `<p>t</p>`). |
| Al guardar (D1) | POST a crear pedido, cotización y producto (incluida `api_crear_producto_rapido`) con `<script>`: lo guardado en la base no lo trae. Lo mismo al editar. |
| Formato permitido | `<p><b>a</b> <i>b</i></p><ul><li>c</li></ul>` sale idéntico. |
| Idempotencia (D1) | Sanitizar dos veces da lo mismo que sanitizar una vez (al guardar y al mostrar se aplican seguidas). |
| Vacío | Un detalle que queda vacío tras sanitizar muestra «Sin especificaciones adicionales.». |
| Copias | Un pedido duplicado o convertido desde una cotización con HTML peligroso guardado directo no lo entrega al navegador. |
| Guardia SQL (D4) | Pasa con el código actual; falla con un texto de ejemplo (dentro de la propia prueba, no en `pedidos/`) que usa un f-string en `execute`. |
| Sin datos tocados (D4) | `makemigrations --check --dry-run` sin cambios; ninguna prueba modifica filas ya guardadas. |
| Existentes | `test_contrato_error.py:126` y la suite completa, con los fallos esperados heredados. |

Nota: las pruebas comprueban el HTML que entrega el servidor; «no se ejecuta» se garantiza porque la etiqueta no llega al navegador. La revisión manual del paso 6 lo confirma a la vista. Si el sanitizador lanza una excepción, **no se captura** (regla 4): el resultado es un error 500 visible, nunca HTML sin limpiar.

## Anexo · consulta de revisión de la réplica (solo lectura, solo conteos; **no ejecutada ni probada** por el agente)

`mysql` y `dbshell` exigen consulta previa incluso en local (`AGENTS.md`, sección 6); la corre el desarrollador en la réplica, nunca en producción. Se repite el mismo bloque para `pedidos_cotizacion` (columna `detalles`) y `pedidos_producto` (columna `descripcion`):

```sql
SELECT 'pedido.detalles_pedido' AS campo,
       COUNT(*)                                                                AS registros,
       SUM(detalles_pedido IS NOT NULL AND detalles_pedido <> '')              AS con_texto,
       SUM(detalles_pedido LIKE '%<script%')                                   AS con_script,
       SUM(detalles_pedido REGEXP '[[:space:]"/]on[a-z]+[[:space:]]*=')        AS con_evento,
       SUM(detalles_pedido LIKE '%javascript:%')                               AS con_javascript,
       SUM(detalles_pedido REGEXP '<(iframe|img|svg|style|table)')             AS con_otras_peligrosas,
       SUM(detalles_pedido REGEXP '<(div|span|a )')                            AS con_div_span_a,
       SUM(detalles_pedido LIKE '%style=%' OR detalles_pedido LIKE '%class=%') AS con_style_o_class,
       MAX(CHAR_LENGTH(detalles_pedido))                                       AS largo_maximo
FROM pedidos_pedido;
```

Solo devuelve conteos y un largo; ningún contenido. Si `con_div_span_a` o `con_style_o_class` son altos, el formato visible podría cambiar con la lista de D3: se detiene y se consulta (no se amplía la lista por cuenta propia).

## Relación con la 04-09 (política de contenido)

La 04-09 activa CSP en modo **solo reporte**: no bloquea nada, así que **no** protege contra XSS mientras exista Summernote y otros CDN con scripts en línea. La sanitización es la defensa real; la CSP estricta (Épica 08, 08-08) será la segunda capa. Ninguna reemplaza a la otra, y el orden (04-07 antes que 04-09) no cambia.

## Verificación en producción (la hace el desarrollador; **no verificado** hasta entonces)

1. Respaldo previo (`respaldo.md`).
2. **Instalar la dependencia en la consola antes del Reload** (paso 0 ya hecho) y confirmar que importa. El import ocurre al sanitizar, no al arrancar: si el Reload va antes que la instalación, las pantallas de detalle y los formularios darían error 500.
3. Tras el Reload: abrir el detalle de un pedido, una cotización y un producto con formato y ver que se ve igual; editar uno sin cambios y guardar.
4. `server.log` sin errores nuevos.
- **No verificado:** si en producción hay HTML guardado después del último refresco de la réplica con etiquetas fuera de la lista blanca; si `nh3` instala en el entorno de la web app (paso 0).

## Plan de retroceso

`retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y Reload. **`nh3` puede quedarse instalado:** el código anterior no lo usa. Con D4 no hay datos que deshacer; lo guardado sanitizado entre el despliegue y el retroceso queda sin las etiquetas quitadas (inofensivo), y al volver a `|safe` lo ya guardado vuelve a imprimirse sin filtro, igual que antes de la iteración. Si el fallo es solo que falta la dependencia (500 en los detalles), basta instalarla y recargar; no hace falta retroceder.

## Criterio de término

- Paso 0 hecho (instalación en PythonAnywhere comprobada).
- Tabla de pruebas en verde; guardia SQL en verde.
- Revisión de la réplica con conteos en la bitácora.
- RDA-020 escrita en `decisiones.md` y `requirements.txt` con versión exacta.
- AUD-03-001 resuelto en la auditoría; verificación de producción hecha.

## Riesgos

- **Perder formato visible:** con la lista exacta de la barra y sin atributos, lo que usara `div`, `span`, `style` o enlaces se verá sin ese formato. Mitigado con la revisión de la réplica antes de ejecutar; si hay conteos altos, se detiene y se consulta.
- **Dependencia nueva en un plan gratuito:** si la rueda no instala en PythonAnywhere, la iteración no se despliega; se comprueba en el paso 0, antes de escribir código.
- **Sanitizar al guardar cambia lo que se guarda:** un usuario que pegue HTML verá menos formato que antes. Esperado.
- **Datos peligrosos ya guardados siguen en la base (D4):** quedan neutralizados solo al mostrarse por la plantilla. Si algún día se leen por otra vía (una exportación, el admin con otro widget, una pantalla nueva), hay que pasar por el mismo filtro. Mitigado: queda dicho aquí y la limpieza se propone aparte si la revisión lo justifica.
- **Doble sanitización (D1):** cuesta poco con textos cortos y es idempotente (prueba).
- **Guardia SQL con falsos positivos:** se ajusta a los casos de la tabla; un `execute` con SQL fijo y parámetros pasa.
- **API de `nh3` inferida:** la firma de `nh3.clean` (`tags`, `attributes`, `clean_content_tags`) viene de mi conocimiento, no se leyó su documentación en esta redacción; se confirma al instalarla (paso 0) y con las pruebas.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-06.
