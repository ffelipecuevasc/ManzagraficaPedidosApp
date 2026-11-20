# Bitácora 04-07 · Sanitización del HTML enriquecido y revisión de inyección SQL

- **Fecha:** 2026-11-20
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** **En revisión, pendiente de despliegue.**
  - Etiqueta prevista: `v4.9-sanitizacion-html`. Retroceso: `v4.8-historial-clientes`.
  - Falta la revisión manual en la réplica, en escritorio y a 360 px (paso 6). La hace el desarrollador.
  - Después, el despliegue con `despliegue.md`, sección 3.14.
- **Regla:** solo conteos, tiempos e identificadores de fila. Ningún contenido, nombre, teléfono ni monto.
- **Marcas:**
  - «Consola»: el desarrollador pegó la salida y se vio.
  - «Dicho»: lo afirma el desarrollador.
  - «Agente»: lo ejecutó el agente en local.
  - «Inferido»: sin verificar.

## Resumen

Se limpia el HTML del editor con `nh3==0.3.8` en dos momentos (RDA-020):

- **Al guardar:** `clean_detalles_pedido`, `clean_detalles` y `clean_descripcion` en los tres formularios.
- **Al mostrar:** el filtro `html_seguro` reemplaza a los tres `|safe`.

La lista blanca es la de la D3, sin atributos. Se agregaron 23 pruebas y una prueba-guardia de SQL con `ast`. No cambia el esquema y no se tocan datos. Las cuatro notas «documentado» quedaron escritas en `docs/operacion/`.

## Estado de partida (agente)

- El repositorio estaba en `main` = `4c35eae`, limpio.
- Había tres `|safe`: `pedido_detail.html:123` (la redacción decía `:115`), `cotizacion_detail.html:150` y `producto_detail.html:53`.
- No había `pedidos/templatetags/`, ningún `mark_safe` en la aplicación, ni `.raw(`, `.extra(` o `RawSQL`.
- La única llamada a `execute` está en `utils.py:301` (la redacción decía `:155-162`) y está parametrizada.

## Paso 0 (consola, 2026-11-20)

- Se instaló en el venv de la web app, con Python 3.13.1.
- `nh3` 0.3.8 vino de una rueda precompilada de 837 kB, sin compilar.
- CPU: 1,17 s (0,931 de usuario y 0,239 de sistema).
- El venv pasó de 135 M a 137 M (`du`, redondeado).
- `nh3.clean('<p>a</p><script>b</script>', tags={'p'})` devolvió `<p>a</p>`.
- En local, el venv tiene `nh3` 0.3.8 desde una rueda `win_amd64` (consola, `pip show`).

## Paso 1: respaldo de la réplica (consola)

`replica_antes_04-07.sql`: 1.537.213 bytes, 19 de 19, `CUMPLE D2`, SHA-256 `BE900C4449AA6FA6F5E2909104DC7E2E43E30885F67E6C94C46BE35E43E8AC16`.

Línea base esperada según la bitácora 04-06: 388 pruebas, `OK (expected failures=3)`.

## Paso 2: revisión del HTML guardado en la réplica (consola)

La réplica es la del refresco del 2026-11-18 14:26:45. Hoy además tiene la `0008` aplicada y un cliente menos. Se usó la consulta del anexo, a la que se le agregó la columna `con_data`.

| Campo | Registros | Con texto | script | evento | javascript | otras peligrosas | div/span/a | style/class | data: | Largo máximo |
| :---- | --------: | --------: | -----: | -----: | ---------: | ---------------: | ---------: | ----------: | ----: | -----------: |
| `pedido.detalles_pedido` | 992 | 964 | 0 | 0 | 0 | 2 | 8 | 12 | 2 | 819.085 |
| `cotizacion.detalles` | 33 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 230 |
| `producto.descripcion` | 60 | 51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 |

**15 pedidos afectados** (consola, solo identificadores y marcas):

- **46 y 56** traen `<img>` y `data:`, con 252.301 y 819.085 caracteres. Son del 2026-01-19.
- **37, 47, 54, 67, 131, 209, 222, 438, 541, 907, 909, 933 y 953** traen solo `div`, `span` o `a`, o `style` o `class`. Ninguno trae tablas, `iframe` ni `svg`.
- Cuatro son recientes: 907, 909, 933 y 953, del 26 de octubre al 6 de noviembre. El editor actual sí genera `div`, `span` y `style`.

**Dicho:** al abrirlos en la réplica, los tres primeros mostraban imágenes grandes, el resto eran descripciones con listas y uno tenía una URL a una imagen.

**Inferido:** las dos imágenes están incrustadas en base64 y esa URL podría ser un `<a href>`, que la D3 deja sin el `href`.

**Decisión del desarrollador (2026-11-20, dicha):**
- Los conteos no son altos y la D3 no se reabre.
- Los pedidos 46 y 56 dejan de mostrar su imagen. Si se editan y se guardan, la D1 la borra de la base.
- El desarrollador guarda una copia de las dos imágenes desde producción y no edita esos pedidos.
- El rescate queda como pendiente sin destino.

## Paso 3: pruebas primero (agente)

`pedidos/tests/test_sanitizacion_html.py` tiene 23 pruebas en cinco clases:

- **La función:** variantes, atributos, `div` y `span`, formato permitido, idempotencia, nulo y vacío.
- **Al mostrar:** HTML guardado directo en la base para los tres detalles, variantes, atributos, formato y el texto por defecto cuando el detalle queda vacío.
- **Al guardar:** crear y editar pedido, cotización y producto, la creación rápida y `test_guardar_elimina_una_imagen_incrustada`.
- **Copias:** pedido duplicado y pedido convertido desde una cotización.
- **Guardia SQL:** pasa con el código actual, detecta los 7 casos prohibidos y acepta SQL fijo con parámetros.

Antes de cablear los formularios y las plantillas, la ejecución dio `Ran 23 tests`, `FAILED (failures=30)`. Fallaron todas las de vistas, guardado y copias, contando las subpruebas. Las de la función y las de la guardia ya pasaban. Con eso quedaron confirmados `attributes={}` y `clean_content_tags` de `nh3` 0.3.8.

En las pruebas de pantalla se buscan marcas únicas (`alert(1)`, `ejemplo.invalid`, `marca-oculta`, `comentario-oculto`) y no las etiquetas, porque `base.html` trae sus propios `<svg>`, `<style>` y comentarios.

## Pasos 4 y 5: implementación (agente)

- `requirements.txt`: `+nh3==0.3.8`, en orden alfabético, ASCII, LF y sin BOM. Quedan 22 líneas.
- `pedidos/sanitizar.py`: `sanitizar_html()` con la importación de `nh3` dentro de la función (regla 8.9). Usa `tags`, `clean_content_tags={'script','style'}`, `attributes={}`, `strip_comments=True` y `link_rel=None`. No captura excepciones (regla 8.4).
- `pedidos/forms.py`: un `clean_<campo>` en cada uno de los tres formularios.
- `pedidos/templatetags/__init__.py` y `html_seguro.py`: el filtro sanitiza y recién entonces aplica `mark_safe`.
- Las tres plantillas pasan a `{% load humanize html_seguro %}` y usan `|html_seguro`. En el pedido se conserva `|default:"Sin especificaciones adicionales."`.
- No se tocaron `views.py`, los modelos, las migraciones ni la configuración.

## Verificación (agente)

| Comando | Resultado |
| :------ | :-------- |
| `python manage.py test pedidos` | `Ran 411 tests`, `OK (expected failures=3)`: R8, R9 y R15, las mismas que en la 04-06 |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |

Las consultas por página no cambian: el filtro no consulta la base.

**Tiempo de sanitizar** (agente, script en la carpeta temporal, local en Windows):

- Texto de 819.106 caracteres: un `<img>` con `data:` de 819.000 más listas y negrita.
- Mediana de 10,6 ms en 10 repeticiones, con mínimo de 10,4 ms y máximo de 14,8 ms.
- El resultado tiene 53 caracteres, sin la imagen.
- Sanitizar de nuevo lo ya limpio tarda 0,07 ms.
- En PythonAnywhere no se midió.

## Notas «documentado» (decisión del 2026-11-17, confirmada el 2026-11-20)

El desarrollador aprobó el archivo nuevo antes de crearlo.

- **`docs/operacion/riesgos-aceptados.md` (nuevo):**
  - AUD-04-003: la búsqueda queda en los registros, riesgo aceptado.
  - AUD-02-030: recuperación de contraseña y acceso del admin, solo documentado.
  - Eliminar una cotización sin evento, decisión explícita.
- **`docs/operacion/respaldo.md`, sección 7:** AUD-02-023, `media/` sin copia. Incluye la diferencia con las imágenes incrustadas de los pedidos 46 y 56.
- Sin hechos nuevos: todo sale de la definición de la Épica 04 y de la auditoría. La protección manual de `media/` (cómo, cada cuánto y dónde) no está escrita en ninguna parte y quedó como `PENDIENTE_DESARROLLADOR`.

## Archivos

| Archivo | Cambio |
| :------ | :----- |
| `requirements.txt` | `+nh3==0.3.8` |
| `pedidos/sanitizar.py` (nuevo) | Función única de sanitización |
| `pedidos/templatetags/__init__.py`, `html_seguro.py` (nuevos) | Filtro `html_seguro` |
| `pedidos/forms.py` | Tres `clean_<campo>` |
| `pedido_detail.html`, `cotizacion_detail.html`, `producto_detail.html` | `\|safe` → `\|html_seguro` |
| `pedidos/tests/test_sanitizacion_html.py` (nuevo) | 23 pruebas |
| `docs/operacion/riesgos-aceptados.md` (nuevo), `respaldo.md` | Notas «documentado» |
| `docs/operacion/despliegue.md` | Sección 3.14 y fila prevista en la sección 5 |
| `_planificacion/00_producto/decisiones.md` | RDA-020 Aceptada (índice y sección) |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-03-001 pasa a corregido en código, pendiente de despliegue. Notas escritas para AUD-02-023, AUD-02-030 y AUD-04-003 |
| `_planificacion/00_producto/registro-pendientes.md` | Encabezado, tabla, pendientes nuevos, historial y próximo hito |
| `iteracion-04-07-…md` | Estado, líneas corregidas, RDA-019, alcance 7, riesgos y criterios |
| Esta bitácora | Nueva |

Fines de línea: `sed -i` dejó en LF algunos archivos que estaban en CRLF en la copia de trabajo. Se volvieron a CRLF con `unix2dos`. Con `core.autocrlf=true`, el diff muestra solo las líneas cambiadas.

## Riesgos y lo que no se vio

- **No visto:** la revisión manual en el navegador (paso 6), el HTML guardado en producción después del 2026-11-18 y el tiempo de sanitizar en el servidor.
- **Hay formato que se pierde** en 13 pedidos, más las imágenes de 46 y 56. Lo decidió el desarrollador.
- **Si el Reload va antes de instalar `nh3`, el arranque no falla:** las pantallas de detalle y los formularios responden 500. Por eso `despliegue.md` 3.14 exige `pip show nh3` antes del Reload.
- **El admin muestra el HTML guardado como texto escapado.** No se sanitiza al guardar desde el admin, porque no usa los formularios de la aplicación. Lo cubre el filtro al mostrar.

## Mensaje de commit sugerido

`Épica 4 - Iteración 04-07: sanitiza el HTML enriquecido con nh3 al guardar y al mostrar, guardia de SQL y notas de riesgos; sin desplegar`
