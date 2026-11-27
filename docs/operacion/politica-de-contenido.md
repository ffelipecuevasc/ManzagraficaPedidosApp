# Política de contenido en observación

Desde la iteración 04-09, la aplicación envía en cada respuesta la cabecera `Content-Security-Policy-Report-Only`. Esta página dice qué hace, cómo leer lo que anota y cómo apagarla.

## Qué es

Una política de seguridad de contenido le dice al navegador de dónde puede cargar scripts, estilos, fuentes e imágenes. En **modo observación** el navegador **no bloquea nada**: solo anota en su consola cada cosa que no cumple. El sitio se ve y funciona igual.

- La política es la que se quiere al final: solo el mismo sitio (`'self'`). Por eso hoy anota todo lo que viene de servidores externos (Google Fonts, Tailwind, jsDelivr, jQuery) y todo lo escrito dentro de las páginas.
- **No protege contra nada.** La defensa contra el HTML peligroso es la sanitización de la 04-07. El modo que bloquea (`SECURE_CSP`) llega en la Épica 08 (08-08), cuando las librerías estén alojadas en el propio sitio.
- No hay un punto que reciba reportes: nada se guarda en la base ni se envía a terceros.
- Se configura en `PedidosApp/settings.py` (`CSP_OBSERVACION` y `SECURE_CSP_REPORT_ONLY`).

## Cómo leer el reporte

1. Abre el sitio (la réplica local o producción) en Chrome y pulsa `F12`.
2. Pestaña **Red**: elige la primera petición de la página (el documento) y mira las cabeceras de la respuesta. Debe traer `Content-Security-Policy-Report-Only` y **no** `Content-Security-Policy`.
3. Pestaña **Consola**, sin filtros: cada infracción empieza con `[Report Only]` y dice qué recurso y qué directiva (`script-src`, `style-src`, `font-src`…). Los mensajes de piezas en línea dicen «inline script», «inline style» o «inline event handler».
4. Si anotas algo, anota **solo conteos y el servidor** (por ejemplo `cdn.jsdelivr.net`). Nunca la dirección completa con parámetros ni textos de la página: pueden traer nombres o teléfonos de clientes.

El inventario completo de la 04-09 está en `_planificacion/10_epicas/epica-04-seguridad/iteracion-04-09-politica-de-contenido-en-observacion.md`, sección «Ejecución y revisión manual».

## Cómo apagarla

Sirve si la consola llena de mensajes estorba o si se sospecha que la cabecera causa un problema (no se espera: no bloquea).

1. En el `.env` del servidor (pestaña **Files** de PythonAnywhere), agrega o cambia esta línea:

   ```
   CSP_OBSERVACION=False
   ```

   Tiene que ser **exactamente** `False`. Cualquier otro valor (`false`, `0`, `no`, vacío) la deja **activa**; ningún valor impide que el sitio arranque.
2. **Un** Reload de la web app, confirmado con «Detectar reinicios de uWSGI» y `DESDE_CL` (`despliegue.md`, 3.6 y 3.14 B, paso 6).
3. **Confírmalo en la pestaña Red:** recarga la página y revisa que la respuesta del documento **ya no trae** `Content-Security-Policy-Report-Only`. En la consola dejan de salir los mensajes `[Report Only]`.

En local, lo mismo con `$env:CSP_OBSERVACION = "False"` en la consola de PowerShell antes de `runserver` (tiene prioridad sobre el `.env`); con `Remove-Item Env:CSP_OBSERVACION` vuelve.

**Para volver a encenderla:** borra la línea del `.env` (o pon `True`) y haz un Reload. La política no deja memoria en el navegador (a diferencia de HSTS): el cambio rige desde la siguiente carga.
