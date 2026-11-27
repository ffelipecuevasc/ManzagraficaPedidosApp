# Iteración 04-09 · Política de seguridad de contenido en observación

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** **En revisión · pendiente de despliegue** (2026-11-27). Código en `main` (`6b6f590`): middleware, `CSP_OBSERVACION` y `SECURE_CSP_REPORT_ONLY` en `settings.py`, `.env.example` (pegado por el desarrollador) y `pedidos/tests/test_csp.py`; 461 pruebas, `OK (expected failures=3)`; revisión manual en la réplica hecha (sección «Ejecución y revisión manual»). Etiqueta propuesta `v4.11-csp-observacion`; retroceso `v4.10-acceso-limites`; procedimiento en `despliegue.md` 3.16. Bitácora: [bitacora-04-09](../../99_bitacora/epica-04-seguridad/bitacora-04-09.md). Antes: ~~Pendiente (redactada, decisiones resueltas).~~ Redactada el 2026-11-17 ([bitacora-04-09-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-09-redaccion.md)); D1 a D4 resueltas por el desarrollador el mismo día ([bitacora-04-09-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-09-cierre.md)).
- **Subfase del plan:** nueva (reorganización del 2026-10-27, RDA-014); `definicion-epica-04.md`, alcance 9 y decisión de la épica sobre la 04-09.
- **Depende de:** la 04-02 (comparte `settings.py` y no repite ninguna de sus cabeceras) y, por orden de despliegue, de todas las anteriores. Se redactó en paralelo a la vigilancia de la 03-05; ~~**su ejecución en local no empieza hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17). **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).**~~ **Superado el 2026-11-18 (RDA-021): no hay vigilancia que cerrar; la 14-01 se despliega antes de la 04-01 (RDA-022).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-10 → … → 04-08 → **04-09**, la última de la Épica 04. **Decisión del desarrollador (2026-11-22, dicha por él; sin RDA): la 04-09 se despliega antes que la 14-04.** Retroceso de la 04-09: `v4.10-acceso-limites`. El retroceso de la 14-04 pasa a ser `v4.11-csp-observacion`, pero eso se ajusta en la Épica 14 (no se tocó aquí).
- **Es requisito de:** la Épica 08 (precondición: «04-09 desplegada») y la 08-08, que reemplaza este modo por la política estricta (registro, fila 08-08).
- **RDA relacionadas:** RDA-007; RDA-016 (interfaz con plantillas del servidor). **Sin RDA nueva:** no hay dependencia ni decisión estructural.
- **Hallazgos que cierra:** ninguno por sí sola (es observación). **Prepara** AUD-03-005 (librerías sin integridad, 08-07 y 08-08) y es la segunda capa de AUD-03-001 (04-07).
- **Cambio de esquema:** ninguno.
- **Respaldo previo al despliegue:** no lo exige (sin migraciones ni datos); se sigue el protocolo normal.
- **Archivos que tocará la ejecución:** `PedidosApp/settings.py` y `.env.example` (**consulta previa**, `AGENTS.md`, sección 6), `pedidos/tests/test_csp.py` (nuevo), una página breve de lectura en `docs/operacion/` y `despliegue.md` si corresponde. **Ninguna plantilla ni archivo de JavaScript** (D2).

## Objetivo

Que el servidor envíe una política de seguridad de contenido **solo para observar**, de modo que el navegador anote en su consola cada recurso externo, cada script y cada estilo en línea que hoy carga la aplicación, **sin bloquear nada** y sin cambiar lo que ve el usuario. Ese inventario es la entrada de la Épica 08.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main`, con archivo y línea. Lo que dice cómo se comporta Django se leyó en el código de Django 6.0.1 instalado en `.venv` (solo lectura; no se ejecutó nada).
- **Inferido:** sale de leer el código o del comportamiento documentado de los navegadores; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor o en un navegador contra el dominio real.

## Qué es y por qué solo observación

Una política de seguridad de contenido (CSP) es una cabecera que le dice al navegador de dónde puede cargar scripts, estilos, fuentes e imágenes. Con la cabecera `Content-Security-Policy` el navegador **bloquea** lo que no cumple; con `Content-Security-Policy-Report-Only` **solo anota** la infracción en su consola y deja pasar todo.

La aplicación hoy no podría usar la versión que bloquea: carga Tailwind, jQuery, Select2, Summernote y SweetAlert2 desde servidores ajenos y tiene scripts y estilos escritos dentro de las páginas. Una política estricta la dejaría sin estilos ni formularios. Por eso la 04-09 solo observa, y el modo que bloquea (`SECURE_CSP`) llega en la Épica 08 (08-08), cuando las librerías estén autoalojadas (08-05 a 08-07).

**Qué defiende y qué no:** en modo observación **no protege contra nada**. La defensa real contra un `<script>` guardado es la sanitización de la 04-07; la CSP será su segunda capa. Esta iteración vale por lo que **enseña**, no por lo que impide.

## Nombres exactos en Django 6.0.1 (verificado en `.venv`)

| Qué | Nombre | Dónde |
| :-- | :----- | :---- |
| Middleware | `django.middleware.csp.ContentSecurityPolicyMiddleware` | `django/middleware/csp.py` |
| Política que bloquea | `SECURE_CSP` (diccionario, por defecto `{}`) | `conf/global_settings.py:669` |
| Política solo de observación | **`SECURE_CSP_REPORT_ONLY`** (diccionario, por defecto `{}`) | `conf/global_settings.py:670` |
| Constantes de valores | `django.utils.csp.CSP`: `CSP.SELF` (`'self'`), `CSP.NONE`, `CSP.UNSAFE_INLINE`, `CSP.NONCE`, `CSP.HEADER_REPORT_ONLY`… | `django/utils/csp.py` |
| Cabecera que emite | `Content-Security-Policy-Report-Only` | `CSP.HEADER_REPORT_ONLY` |
| Procesador de contexto del nonce | `django.template.context_processors.csp` (entrega `csp_nonce`) | `template/context_processors.py:93` |
| Decoradores por vista | `csp_override` y `csp_report_only_override` | `views/decorators/csp.py` |

Comportamiento comprobado en el código del middleware:

- Una configuración **vacía** no agrega cabecera: con `SECURE_CSP_REPORT_ONLY = {}` no hay nada que enviar (es el interruptor de apagado, D3).
- Si la respuesta ya trae la cabecera, el middleware **no la pisa** (una vista puede fijar la suya).
- El nonce es perezoso: solo se genera si la política lleva `CSP.NONCE` **y** alguien lo usa; sin él, no cuesta nada.
- El middleware solo actúa en `process_response`: no hay restricción de orden, y no consulta la base.
- **No hay comprobación de `check --deploy` sobre CSP** (búsqueda en `core/checks`: sin resultados): no cambia la lista de advertencias de la 04-02.

## Qué hay hoy (verificado)

### Configuración

- `settings.py` **no define** `SECURE_CSP` ni `SECURE_CSP_REPORT_ONLY`, y `MIDDLEWARE` (`settings.py:69-77`) no incluye el middleware de CSP; los procesadores de contexto (`:88-92`) no incluyen `csp`.
- **Cabeceras que ya existen y esta iteración no repite:** `XFrameOptionsMiddleware` está en `MIDDLEWARE` (`settings.py:76`) y `X_FRAME_OPTIONS` vale `DENY` por defecto (`global_settings.py:443`); `SecurityMiddleware` ya aplica `nosniff`, la política de referente `same-origin` y `Cross-Origin-Opener-Policy: same-origin` (`global_settings.py:656-662`). La 04-02 agrega HSTS, la redirección a HTTPS y las cookies seguras. **La 04-09 solo agrega la cabecera de observación.** No incluye `upgrade-insecure-requests` (es de la 04-02/HTTPS) ni `frame-ancestors` (ya lo cubre `X-Frame-Options`, y el navegador lo ignora en modo observación: inferido del estándar, no verificado).

### Recursos externos (todos cargados en el navegador; `base.html` y `login.html`)

| Archivo y línea | Recurso | Directiva que lo gobernaría |
| :-------------- | :------ | :-------------------------- |
| `base.html:9-10` | `preconnect` a `fonts.googleapis.com` y `fonts.gstatic.com` | `connect-src` (puede aparecer o no; no verificado) |
| `base.html:11-12` | Hoja de estilos de Google Fonts (Bebas Neue, Inter) | `style-src`; las fuentes en sí, `font-src` (`fonts.gstatic.com`) |
| `base.html:14` | Material Icons Round (Google Fonts) | `style-src` y `font-src` |
| `base.html:16` | Tailwind en el navegador, `cdn.tailwindcss.com` | `script-src`; además **genera estilos en tiempo de ejecución** (`style-src`) |
| `base.html:37` | Select2, hoja de estilos, `cdn.jsdelivr.net` | `style-src` |
| `base.html:38` | Summernote Lite, hoja de estilos, `cdn.jsdelivr.net` | `style-src` y, por sus tipografías de iconos, probablemente `font-src` (no verificado) |
| `base.html:325` | jQuery 3.7.1, `code.jquery.com` | `script-src` |
| `base.html:326` | Select2, script, `cdn.jsdelivr.net` | `script-src` |
| `base.html:327` | Summernote Lite, script, `cdn.jsdelivr.net` | `script-src` |
| `base.html:328` | SweetAlert2 11, `cdn.jsdelivr.net` | `script-src` (inyecta además su propia hoja de estilos: no verificado) |
| `login.html:10-12`, `:15`, `:17`, `:147` | Lo mismo que `base.html` para el acceso, que **no** extiende la plantilla base: preconnect, Google Fonts, Material Icons, Tailwind y jQuery | las mismas |

- **Cinco servidores ajenos:** `fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.tailwindcss.com`, `cdn.jsdelivr.net` y `code.jquery.com`. Ningún recurso externo lleva `integrity` (AUD-03-005).
- **Mismo origen (no generan reporte):** `base.html:8` (ícono), `:40` (`index.css`), `:329` (`index.js`); `login.html:9`, `:37`, `:148`.
- **Enlaces que no gobierna la política** (navegación, no carga de recursos; inferido del estándar): `base.html:280` (LinkedIn), `pedido_detail.html:248` y `estadisticas_pagos.html:253` (`https://wa.me/…`).
- **Imágenes subidas:** viven en `/media/` del mismo origen (`linea-base-produccion.md`, línea 141: PythonAnywhere las sirve por el mapa de estáticos).

### Scripts en línea (dentro de las páginas)

| Archivo y líneas | Qué es |
| :--------------- | :----- |
| `base.html:17-36` | Configuración de Tailwind (`tailwind.config = {…}`) |
| `login.html:18-36` | La misma configuración de Tailwind |
| `login.html:149-181` | Bloqueo del doble envío del acceso |
| `pedido_form.html:436-468` | Bloqueo del doble envío del pedido (00-07) |
| `pago_form.html:141-152` | Script del formulario de pago |
| `producto_form.html:127-148` | Script del formulario de producto |
| `restaurar_bd.html:59-90` | Confirmación con SweetAlert2 de la restauración |

**Ninguno de los siete tiene etiquetas de plantilla** (`{{` o `{%`, contadas en cada rango el 2026-11-17: 0): son texto fijo. Eso importa para la Épica 08: se pueden mover a archivos estáticos sin perder nada.

### Estilos en línea

- **Bloques `<style>`:** `login.html:39-54` y `trabajo_semanal.html:7-12`. (`cotizacion_pdf.html:7` es la plantilla que convierte WeasyPrint en el servidor: el navegador no la ve y no le afecta la política.)
- **Atributos `style="…"` en pantallas del navegador (8):** `dashboard.html:128` (degradado cónico) y `:190` (ancho calculado); `estadisticas_bd.html:112`, `:113` y `:128` (degradados y retraso de animación del gráfico); `estadisticas_pagos.html:157`, `:168` y `:179` (anchos por porcentaje). Varios llevan valores calculados por el servidor. (`cotizacion_pdf.html` tiene 10 más, del PDF.)
- **Estilos asignados desde JavaScript** (`index.js:820-836`, `boton.style.cursor` y `.opacity`): se asignan por el modelo de objetos de estilos, que la política **no** bloquea (inferido del estándar; se confirma en la observación).

### Manejadores de eventos en línea

| Archivo y línea | Manejador |
| :-------------- | :-------- |
| `pago_detail.html:24`, `pedido_detail.html:18` | `onclick="window.print()"` |
| `respaldar_bd.html:19` | `onclick="setTimeout(function(){ location.reload(); }, 2000);"` (la **04-01 lo retira**, AUD-03-002) |
| `errors/500.html:23` | `onclick="location.reload()"` |
| `index.js:566`, `:567`, `:574` | `onchange`, `onkeydown` y `onclick`, **generados dentro de texto HTML por el JavaScript** (filas de ítems del pedido) |

Los manejadores en línea **no los cubre un nonce**: cuando llegue la política estricta habrá que reemplazarlos por escuchas de eventos en JavaScript (o aceptar `unsafe-hashes`).

### JavaScript propio

- `index.js` (870 líneas): no usa `eval`, `new Function`, `document.write` ni `setTimeout` con texto (búsqueda). Las llamadas a la red son `fetch` al mismo origen (`index.js:233`, `:642`, rutas `api/…`).
- **Lo que no se ve desde el repo:** si las librerías externas usan `eval`, inyectan estilos o crean iframes (Select2, Summernote, SweetAlert2, el Tailwind del navegador). **Se descubre en la observación.**

## Política mínima de observación

La política debe ser la **que querremos al final**, sin los servidores externos. Si se escribiera con la lista de los cinco servidores actuales, el navegador no anotaría nada y la observación no enseñaría nada. Con la política final, **cada recurso ajeno y cada línea en línea aparece como una infracción anotada**, que es justo el inventario que se busca.

```python
from django.utils.csp import CSP

SECURE_CSP_REPORT_ONLY = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF],
    "img-src": [CSP.SELF, "data:"],
    "font-src": [CSP.SELF],
    "connect-src": [CSP.SELF],
    "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "form-action": [CSP.SELF],
}
```

- Sin `report-uri` ni `report-to`: **no hay punto de recepción** (D4).
- `img-src` admite `data:` porque las librerías suelen incrustar íconos en ese formato (no verificado); si la observación muestra que no hace falta, la 08-08 lo quita.
- `form-action 'self'` cubre los formularios de la 04-01 (mismos orígenes; en producción el esquema es HTTPS en ambos lados).
- El middleware va **justo después de `SecurityMiddleware`**; el orden no es obligatorio (solo actúa al responder), se fija para que quede junto a las demás cabeceras de seguridad.
- Esta forma es una **propuesta**: los nombres de directivas son los del estándar; qué directivas quedan en la política definitiva lo decide la 08-08 con lo que muestre la observación.

## Cómo se lee el reporte (sin punto de recepción)

1. En la réplica local (`runserver`), abrir las herramientas del navegador (pestaña **Consola**). Cada infracción aparece como un mensaje que empieza por `[Report Only]` y dice qué recurso y qué directiva (comportamiento habitual de los navegadores; inferido, se confirma en la ejecución).
2. Recorrer, con la consola abierta y sin filtros, estas pantallas: acceso, panel, lista y detalle de pedidos, crear y editar pedido (con ítems y el editor), cotizaciones (lista, detalle, crear), productos (lista, crear, detalle), clientes, pagos (lista, ingresar), las tres de estadísticas, trabajo semanal, base de datos (respaldar, restaurar, estadísticas) y las páginas 404 y 500. No se usa la búsqueda con datos reales: sus textos llevan nombres y teléfonos.
3. Anotar en la bitácora **solo conteos**: infracciones por directiva y por servidor, y cuáles son en línea. Nada de URLs con parámetros ni contenido de clientes (`AGENTS.md`, sección 7, regla 4).
4. **Sin punto de recepción** (D4): no se agrega una vista que reciba reportes (tendría que escribir en una tabla, con retención y purga, regla 8.11, y es CPU del único worker, regla 8.10) ni se usa un servicio de terceros (regla 8.10: la lista de salida de PythonAnywhere lo impide).
5. En producción, el mismo mensaje aparece al abrir el sitio con la consola abierta; no hace falta para construir el inventario (las plantillas son las mismas), solo para confirmar que la cabecera llega (verificación en producción).

## Efecto sobre lo que ya existe

- **Todas las páginas:** ninguno. Una política de observación **no bloquea** (por definición de la cabecera; inferido del estándar, se confirma con la revisión manual: todo debe verse y funcionar igual). Cambia el tamaño de cada respuesta en unos 250 bytes.
- **Summernote y Select2:** sus scripts y estilos de `cdn.jsdelivr.net` aparecerán como infracciones; el editor sigue funcionando. Lo que haga Summernote por dentro (estilos en línea del editor, iconos por fuente) saldrá en el reporte, que es el dato que la 08-07 necesita para decidir qué librerías se mantienen.
- **Formularios de la 04-01 (botones como formularios POST):** los envía el mismo origen; `form-action 'self'` no marca nada. Si el script de confirmación (`data-confirm`, `index.js:357`) crea elementos con manejadores en línea, aparecerán.
- **04-07 (sanitización):** hace que el HTML escrito por usuarios llegue sin `style`, `on…` ni `<script>`; sin ella, esos textos habrían generado infracciones ajenas a la aplicación. Por eso la 04-07 va antes (orden de despliegue ya fijado).
- **04-08:** las páginas de acceso nuevas (mensaje de bloqueo) siguen la misma plantilla `login.html`: sin cambios en el inventario.
- **PDF de cotizaciones:** WeasyPrint genera el PDF en el servidor, sin navegador ni política; la respuesta lleva la cabecera, que es inerte (inferido).
- **Panel de administración de Django:** la política también se aplica a sus páginas; es posible que muestre infracciones propias de Django (no verificado). No afecta el inventario de la aplicación.
- **Costo:** sin consultas a la base; el nonce no se genera (la política no lo pide). El middleware agrega un módulo pequeño al arranque (no medido).

## Nonces frente a código en línea

Un nonce es una marca aleatoria por respuesta que permite ejecutar **un script o estilo en línea concreto** sin abrir la puerta a los demás. Lo que cubre y lo que no, con esta aplicación:

| Pieza en línea | ¿Lo cubre un nonce? | Alternativa más sólida |
| :------------- | :------------------ | :--------------------- |
| 7 bloques `<script>` (sin variables de plantilla) | Sí | **Mover a archivos estáticos** (`index.js` u otros): se elimina el problema |
| 2 bloques `<style>` | Sí | ~~Mover a `index.css`~~ **Corregido el 2026-11-22:** el de `login.html` se puede mover a `index.css`; el de `trabajo_semanal.html:7-12` **usa `{{ nivel_presion }}`** en un `conic-gradient`, así que **no se pasa tal cual a `index.css`** (variable CSS fijada por un atributo, clases por tramos o nonce: decisión de la 08-08) |
| 8 atributos `style="…"` con valores del servidor | **No** | Clases de CSS por tramos o `style-src-attr` aceptando el riesgo, decisión de la 08-08 |
| Manejadores `onclick`/`onchange`/`onkeydown` (~~4 en plantillas~~ **6: 3 en plantillas** (la 04-01 retiró el de `respaldar_bd.html`) **y 3 generados por JavaScript**, corregido el 2026-11-22) | **No** | Escuchas de eventos en `index.js` |
| Estilos que inyectan las librerías (Tailwind del navegador, SweetAlert2) | No | Compilar Tailwind en local (08-05); SweetAlert2 autoalojado |

Un nonce exigiría, además, agregar el procesador `csp` a `TEMPLATES` y un atributo en cada bloque (editar 8 plantillas que la 04-01, la 04-04 y la 04-07 también tocan) y **dejaría sin aparecer en el reporte** justo lo que se quiere listar. Y como la Épica 08 mueve las plantillas a parciales (08-03, 08-04) y compila Tailwind (08-05), conviene aplicar los nonces, y los que queden, una sola vez, ahí (la definición de la Épica 08 ya lo prevé en la 08-08).

## Contradicciones con la planificación

- **La definición dice «para conocer qué recursos carga la aplicación»**: solo se logra si la política observada es la **final** (sin servidores externos). Con una política que permitiera los CDN actuales no habría nada que anotar. Se fija así (sección «Política mínima»).
- **La definición pide la política «sin bloquear nada mientras existan los CDN»**: coincide; el bloqueo queda para la 08-08.
- **`login.html` no extiende `base.html`**: repite su `<head>` (fuentes, Tailwind, jQuery). El inventario tiene que mirar las dos plantillas; la 08-02 y la 08-03 la unifican.
- **Fila 04-09 del registro:** dice «Depende de 04-02». Se mantiene, y se agrega que el despliegue va después de la 04-08 por el orden de la épica.

## Fuera de alcance

- La política estricta (`SECURE_CSP`), los nonces y mover scripts o estilos (Épica 08, 08-08).
- Autoalojar librerías y fuentes, y la integridad de subrecursos (AUD-03-005; 08-05 a 08-07).
- Un punto de recepción de reportes y cualquier servicio de terceros.
- Otras cabeceras (`Permissions-Policy`, `Cross-Origin-Embedder-Policy`); las de la 04-02.
- Cambiar plantillas o JavaScript.

## Alcance

1. Agregar `django.middleware.csp.ContentSecurityPolicyMiddleware` a `MIDDLEWARE`, después de `SecurityMiddleware`.
2. Definir `SECURE_CSP_REPORT_ONLY` con la política mínima (D1). **No** definir `SECURE_CSP`.
3. Interruptor de apagado por variable de entorno (D3), sin valor real en `.env.example`.
4. Prueba automatizada de la cabecera (sección «Pruebas»).
5. Recorrer las pantallas con la consola abierta en la réplica y anotar conteos (sección «Cómo se lee el reporte»).
6. Página breve en `docs/operacion/` con cómo leer el reporte y cómo apagarlo.
7. **Fuera:** lo de la sección «Fuera de alcance».

## Decisiones (resueltas por el desarrollador, 2026-11-17)

| # | Decisión | Resuelta como |
| :- | :------- | :------------ |
| D1 | Qué política se observa | **La política final**, solo `'self'` y sin servidores externos (opción A), como en la sección «Política mínima». El navegador anota cada recurso externo y cada pieza en línea. |
| D2 | Nonces y código en línea | **Sin nonces** ni cambios en plantillas en esta iteración (opción A). La Épica 08 mueve los scripts y estilos a archivos y aplica nonces solo a lo que quede (08-08). |
| D3 | Interruptor de apagado | **Variable `CSP_OBSERVACION`**, activa por defecto (también en local, donde se lee el reporte) e **independiente de `SEGURIDAD_PRODUCCION`** de la 04-02. Con `False`, `SECURE_CSP_REPORT_ONLY` queda vacío y no se envía cabecera (comportamiento verificado del middleware). |
| D4 | Dónde se lee el reporte | **Consola del navegador en la réplica** (opción A), sin punto de recepción. |

**Qué se descartó (para no volver a discutirlo):** observar la política actual con los cinco servidores permitidos (no anotaría los recursos externos), dos cabeceras de observación a la vez, nonces y hashes ahora, depender de `SEGURIDAD_PRODUCCION` (la réplica no vería nada), una vista propia que reciba reportes (tabla con retención y trabajo en el único worker) y un servicio de terceros (regla 8.10 y lista de salida de PythonAnywhere).

## Pasos

0. Consulta previa para editar `settings.py` y `.env.example` (`AGENTS.md`, sección 6).
1. Línea base: `test pedidos` (número y fallos esperados tras la 04-08) y `check`.
2. Pruebas primero (tabla siguiente); ver fallar las de cabecera.
3. `settings.py`: middleware, política y variable (D3). `.env.example` con `CSP_OBSERVACION` sin valor real.
4. Revisión manual en la réplica: recorrer las pantallas con la consola abierta (escritorio y 360 px), comprobar que **todo funciona igual que antes** (editor, selectores de cliente y producto, confirmaciones, PDF) y anotar conteos por directiva y servidor.
5. `docs/operacion/`: lectura del reporte y apagado.
6. Bitácora (con conteos, sin URLs con datos), registro, estado «En revisión». Al cerrar la 04-09 queda lista la **revisión final de la Épica 04**.

## Pruebas

| Punto | Prueba |
| :---- | :----- |
| Cabecera presente | `GET /accounts/login/` (pública): trae `Content-Security-Policy-Report-Only` con cada directiva de D1. Igual en una pantalla autenticada (el panel) y en una 404. |
| Nunca bloquea | En esas mismas respuestas **no** hay cabecera `Content-Security-Policy`; y `settings.SECURE_CSP` es `{}` (nada se aplica hasta la Épica 08). |
| Sin reporte externo | La política no contiene `report-uri`, `report-to` ni nombres de servidores externos. |
| Sin duplicados con la 04-02 | No contiene `upgrade-insecure-requests` ni `frame-ancestors`; `X-Frame-Options` sigue siendo `DENY`. |
| Orden | `MIDDLEWARE` contiene el middleware de CSP una vez y después de `SecurityMiddleware`. |
| Apagado (D3) | Con `CSP_OBSERVACION` en `False`, la configuración queda vacía y la respuesta no trae la cabecera (prueba con un proceso hijo que importa la configuración, como la 04-02, y con `override_settings(SECURE_CSP_REPORT_ONLY={})` en el cliente de pruebas). |
| Sin efecto en el resto | Suite completa con los mismos fallos esperados que deje la 04-08; ninguna respuesta cambia de código ni de contenido. |

Nota: las pruebas comprueban la **cabecera**; lo que el navegador anota o no bloquea solo se ve en la revisión manual del paso 4.

## Verificación en producción (la hace el desarrollador; todo **no verificado** hasta entonces)

1. Etiqueta anotada antes del despliegue (RDA-007) y `CSP_OBSERVACION` sin definir o en `True` en el `.env` del servidor.
2. Tras el Reload: abrir el acceso y el panel con la consola abierta; en la pestaña **Red**, la respuesta debe traer `Content-Security-Policy-Report-Only` (confirma que el proxy de PythonAnywhere no la quita) y la consola, mensajes `[Report Only]`. **El sitio debe verse y funcionar igual que antes.**
3. `server.log` sin errores nuevos.
- **No verificado:** que el proxy de PythonAnywhere entregue la cabecera intacta; qué versiones de navegador usa el cliente (la cabecera de observación es antigua y común; inferido); las infracciones propias de las librerías y del panel de administración.

## Plan de retroceso

- **Sin tocar el código (D3-A):** `CSP_OBSERVACION=False` en el `.env` del servidor y Reload; la cabecera deja de enviarse.
- **Con código:** `retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y Reload.
- **A diferencia de HSTS** (04-02), la política de observación **no deja memoria en el navegador**: se evalúa en cada respuesta, así que el retroceso es inmediato en la siguiente carga (inferido del estándar).
- No hay datos que deshacer.

## Criterio de término

- Pruebas de la cabecera en verde; resto de la suite sin cambios.
- Revisión manual en la réplica hecha, con conteos en la bitácora y el sitio funcionando igual.
- Verificación 2 de producción hecha (cabecera presente, sitio sin cambios).
- Definición de la épica: «la política está activa en modo observación en producción».

## Riesgos

- **Falsa sensación de seguridad:** observar no protege. Queda dicho aquí; la protección es la 04-07 y, luego, la 08-08.
- **Ruido en la consola:** decenas de mensajes por pantalla para quien abra las herramientas del navegador. Esperado; se apaga con D3.
- **Que la cabecera no pase el proxy:** se detecta en la verificación 2; no daña nada.
- **Una política mal escrita:** una directiva con error de forma la ignora el navegador (no rompe nada, solo quita observación). La prueba comprueba las directivas exactas.
- **Confundirla con el modo que bloquea:** el nombre de la cabecera y de la configuración lo distinguen; una prueba exige que `SECURE_CSP` siga vacío.
- **Cambios en archivos de configuración:** `settings.py` y `.env.example` exigen consulta previa; `settings.py` también lo editan otras iteraciones de la épica (se parte de lo que dejen).
- **Que alguien la «active» antes de la Épica 08:** pasar la política a `SECURE_CSP` hoy dejaría la aplicación sin estilos ni formularios; la prueba de «nunca bloquea» lo impide.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-08.

## Ejecución y revisión manual (2026-11-22 a 2026-11-27)

«Consola»: salida vista por el agente. «Dicho»: lo afirma el desarrollador (informe de la revisión manual, pegado el 2026-11-27). «No consta»: nadie lo comprobó.

### Ubicación en `main` tras la 04-08 (consola, 2026-11-22)

Las líneas citadas arriba son del 2026-11-17. Las que se movieron: `MIDDLEWARE` en `settings.py:120-132` antes del cambio (ahora el de CSP en `:125`, justo después de `SecurityMiddleware`), procesadores de contexto en `:143-147` (sin `csp`); `login.html` jQuery `:158`, `index.js` `:159`, script contra el doble envío `:160-192`; `pedido_form.html:437-469`; `pago_form.html:145-156`; `restaurar_bd.html:67-100`; `pedido_detail.html:256` (`wa.me`); `index.js` con 897 líneas, manejadores generados en `:584`, `:585` y `:592`. El bloque de bloqueo de la 04-08 en `login.html` no agrega nada en línea.

### Pruebas (consola, agente)

- Línea base: `check` sin problemas; 446 pruebas, `OK (expected failures=3)`.
- `pedidos/tests/test_csp.py` antes de implementar: 15 pruebas, `FAILED (failures=13, errors=1)` (contando subpruebas); pasaban las 6 que ya se cumplían sin el cambio.
- Después: 461 pruebas, `OK (expected failures=3)`; `check` sin problemas; `makemigrations --check --dry-run` → `No changes detected`. Sin migraciones.
- Interruptor (C2, decisión del desarrollador del 2026-11-22): solo el texto exacto `False` apaga; `false`, `0`, `no`, `FALSE`, ` False`, `True` y vacío dejan la política activa y el sitio arranca (prueba con proceso hijo).

### Revisión manual en la réplica (dicho)

18 de 18 pantallas, 24 páginas, en escritorio y a 360 px. Paridad «con diferencias aceptadas» (solo Python 3.13.0 frente a 3.13.1, aceptada en la 00-03). `.env` local sin `CSP_OBSERVACION` y con `DEBUG=True`.

- **Pantalla (dicho):** en `/accounts/login/` llega `Content-Security-Policy-Report-Only` con las 9 directivas, no llega `Content-Security-Policy` y `X-Frame-Options` es `DENY`. En la pestaña Red, los scripts vienen de `cdn.tailwindcss.com`, `code.jquery.com` y `cdn.jsdelivr.net`, y las 3 fuentes de `fonts.gstatic.com`. Con `CSP_OBSERVACION=False` en la consola de PowerShell desaparecen todos los `[Report Only]`; al quitarla vuelven.
- **Criterio de conteo:** cada página cuenta por separado; en la Tabla A, cada combinación de directiva y servidor cuenta una vez por página; en «En línea» y en la Tabla B, cada pieza distinta (por línea o por hash) una vez por página; los mensajes idénticos repetidos, una vez. La #16 (diálogo `data-confirm`) es una acción sobre una página ya contada.

**Tabla A · infracciones por directiva y origen** (número de páginas, sin el admin)

| Directiva | fonts.googleapis.com | fonts.gstatic.com | cdn.tailwindcss.com | cdn.jsdelivr.net | code.jquery.com | En línea | `data:` u otro |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| script-src | 0 | 0 | 23 | 22 | 23 | 33 | 0 |
| style-src | 23 | 0 | 0 | 22 | 0 | 154 | 0 |
| font-src | 0 | 23 | 0 | 0 | 0 | 0 | 0 |
| connect-src | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| img-src | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| otra | — | — | — | — | — | — | — |

**Tabla B · en línea, por tipo**

| Tipo | Total | Páginas |
| :-- | :-: | :-- |
| Script en línea | 29 | Todas las con sesión, el de la configuración de Tailwind (1 por página); además el acceso (2), los formularios de pedido (#5 y #6), de producto (#9b) y de pago (#11b), y restaurar (#15) |
| Manejador en línea | 4 | #4 (1 mensaje), #5 (13), #6 (13), #11c (1) |
| Estilo en línea de plantilla | 13 | #1 (1 bloque `<style>`), #2 (6 atributos `style`), #12b (3), #12c (2), #13 (1 bloque `<style>`) |
| Estilo inyectado por el Tailwind del navegador | 92 | Las 23 páginas HTML, de 3 a 7 por página |
| Estilo inyectado por SweetAlert2 | 37 | 22 páginas, 1 o 2 por página |
| Estilo inyectado sin origen (probablemente Select2 o Summernote) | 12 | #5, #6, #7c, #9b (2 cada una), #10a, #11b, #12c, #15 (1 cada una) |
| `eval` u otro | 0 | — |

**Tabla C · funcionamiento (dicho):** nada se vio ni funcionó distinto por la política; ningún 500; a 360 px todo igual y sin mensajes distintos. Editor, selectores, creación rápida de cliente y producto, ítems, PDF (sin infracciones: el navegador lo abre como PDF), confirmaciones de SweetAlert2 y `data-confirm` (abiertas y canceladas) funcionan. Las fallas vistas en #11 y #12 se repiten idénticas con `CSP_OBSERVACION=False`: son anteriores (hallazgos, abajo).

**Fuera del inventario:**
- **#17, admin:** 0 infracciones (consola vacía).
- **#18, 404 y 500:** no revisadas en la réplica (con `DEBUG=True`, Django muestra su propia página).

**Aclaraciones:**
- (a) Los **11 atributos `style` observados** (#2: 6, #12b: 3, #12c: 2) son los **8 del código** repetidos por bucles: en el panel, 2 en el código se renderizan 6 veces; en estadísticas de la base de datos, los puntos del gráfico. **No es discrepancia.**
- (b) Los **manejadores de #5 y #6 son por instancia** (uno por fila de ítem: 13 mensajes). **El inventario conserva 6** (3 en plantillas y 3 generados por `index.js`). El «Recargar» de `500.html` quedó sin revisar (#18).

**No consta:** las páginas 404 y 500 de la aplicación; las infracciones en producción (verificación 2, al desplegar); qué librería inyecta los 12 estilos sin origen.

### Insumo para la 08-08 (inventario confirmado)

7 scripts en línea (ninguno con variables de plantilla), 2 bloques `<style>` (el de `trabajo_semanal.html` con `{{ nivel_presion }}`), 8 atributos `style`, 6 manejadores en línea (3 en plantillas, 3 generados por `index.js`) y 5 servidores externos (`fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.tailwindcss.com`, `cdn.jsdelivr.net`, `code.jquery.com`). Además: estilos inyectados por el Tailwind del navegador, SweetAlert2 y (probablemente) Select2 o Summernote. Sin `connect-src`, `img-src`, `data:` ni `eval` observados, así que la 08-08 puede evaluar quitar `data:` de `img-src`.

### Hallazgos anteriores a la 04-09 (fuera de alcance, abiertos)

AUD-05-025 (ícono de calendario en modo oscuro), AUD-05-026 (fecha de entrega vacía al editar un pedido), AUD-05-027 (`$ is not defined` en «Ingresar pago»; enlazado con la 08-08), AUD-05-028 (imprimir detalle de pago en blanco), AUD-05-029 y AUD-05-030 (gráficos SVG de estadísticas; causa probable común: localización de números). Del 027 al 030, comprobados con `CSP_OBSERVACION=False` (dicho). Detalle en `auditoria-tecnica.md`.

### Criterios de término

| Criterio | Estado |
| :-- | :-- |
| Pruebas de la cabecera en verde; resto sin cambios | Hecho (consola): 461, `OK (expected failures=3)` |
| Revisión manual en la réplica con conteos y el sitio igual | Hecho (dicho) |
| Verificación 2 de producción (cabecera presente, sitio igual) | **Pendiente** (despliegue, `despliegue.md` 3.16) |
| «La política está activa en modo observación en producción» | **Pendiente** (despliegue) |
| `.env.example` con `CSP_OBSERVACION` sin valor real | Hecho (desarrollador, `6b6f590`; el agente no lo leyó por permisos) |
| Página en `docs/operacion/` | Hecho: [politica-de-contenido](../../../docs/operacion/politica-de-contenido.md) |
