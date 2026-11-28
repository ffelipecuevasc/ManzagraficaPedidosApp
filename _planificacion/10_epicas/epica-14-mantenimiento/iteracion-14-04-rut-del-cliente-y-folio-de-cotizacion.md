# Iteración 14-04 · RUT del cliente y folio de cotización

- **Épica:** 14 · Mantenimiento: errores y mejoras puntuales
- **Estado:** **En revisión (2026-11-27):** implementada en local, 500 pruebas `OK (expected failures=3)`, migraciones `0010_rut_y_folio`, `0011_folio_igual_id` y `0012_folio_unico` (Clase 2, datos, Clase 2; sin `MODIFY`). ~~Faltan el ensayo en la réplica, la revisión manual y el despliegue~~ **2026-11-28: ensayo en la réplica y revisión manual (escritorio y 360 px) comprobados en la consola del desarrollador** (evidencia, A1, A2 y A2b); faltan los avisos, la hora y el despliegue ([bitacora-14-04-implementacion](../../99_bitacora/epica-14-mantenimiento/bitacora-14-04-implementacion.md); `despliegue.md` 3.17). Antes: ~~**Pendiente (redactada, análisis hecho el 2026-11-27).**~~ ~~La implementación espera a que la migración `0009` de la 04-08 exista en `main` (verificado el 2026-11-20 sobre `6b79f63`: la última migración es `0008_proteger_historial_cliente.py`).~~ **La espera está cumplida:** la `0009_acceso_bloqueado.py` existe en `main` y está aplicada en producción (`v4.10-acceso-limites`, 2026-11-21); verificado en `pedidos/migrations/` el 2026-11-27 sobre `e670cef`. ~~La implementación queda en espera de las decisiones del análisis (AUD-05-026 y avisos 1 y 2)~~ **Decisiones del análisis resueltas el 2026-11-27 (dichas por el desarrollador); lista para implementar**: [bitacora-14-04-analisis](../../99_bitacora/epica-14-mantenimiento/bitacora-14-04-analisis.md), «Decisiones del 2026-11-27». AUD-05-026 queda Media y se arregla **después** de esta iteración, en una propia (14-05, número al redactarla).
- **Origen:** pedido del cliente del 2026-11-20, dicho por el desarrollador: (1) que la cotización y su PDF muestren el RUT del cliente; (2) que la numeración de las cotizaciones parta en 1000.
- **Tipo:** mejora puntual (RDA-024). **Sin AUD:** no es un hallazgo de auditoría.
- **Numeración:** 14-04. El 14-03 no se reasigna (RDA-022, punto 4).
- **Depende de:** 04-07 (`v4.9-sanitizacion-html`) y 04-08 desplegadas. La 04-08 trae la migración `0009`; las de esta iteración van después (`0010` a `0012`), para que el orden de despliegue y el de las migraciones coincidan.
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-014 (numeración), RDA-021 (sin esperas), RDA-022 y RDA-024 (destino en la Épica 14).
- **Cambio de esquema:** sí. Tabla nueva `SecuenciaFolio` y columnas nuevas `Cliente.rut` y `Cotizacion.folio`. Clasificación declarada: ver «Clasificación de las migraciones»; se confirma con `sqlmigrate` antes de aplicar.
- **Respaldo previo al despliegue:** **obligatorio y verificado**, y respaldo posterior verificado (con 20 tablas).
- **Etiqueta y retroceso:** etiqueta propuesta **`v14.3-rut-y-folio`** (`despliegue.md`, sección 1: fase 14, correlativo siguiente a `v14.2-duplicar-items`). Destino de retroceso: **`v4.11-csp-observacion`** (2026-11-27). Antes: ~~la etiqueta que deje la 04-08 (aún sin fijar).~~
- **Archivos que tocará la ejecución:** `pedidos/models.py`, módulo nuevo `pedidos/validadores.py`, `pedidos/forms.py`, `pedidos/admin.py`, `pedidos/views.py` (crear, editar, listar, detalle, PDF, convertir y crear cliente rápido), migraciones `0010` a `0012`, plantillas `cotizacion_*.html`, `cotizacion_pdf.html` y de clientes, **`pedido_form.html`** (modal de cliente rápido; H2, 2026-11-27), `pedidos/static/pedidos/js/index.js` (envía el RUT desde los dos modales), `pedidos/tests/factorias.py` (RUT sintético), `scripts/verificar_respaldo.py` y sus pruebas, `docs/operacion/despliegue.md`, `docs/operacion/respaldo.md` y pruebas nuevas.

## Objetivo

Que cada cliente tenga RUT y que la cotización (pantalla y PDF) lo muestre, y que cada cotización tenga un folio correlativo propio, distinto de su clave primaria, que el negocio pueda hacer partir en 1000 sin que el código sepa de ese número.

## Decisiones resueltas (desarrollador, 2026-11-20, dichas por él)

- **D1 · RUT obligatorio** en `Cliente`. Los clientes existentes reciben el ficticio `00.000.000-0` como texto, para que el dueño los reconozca y los corrija (trabajo manual suyo, no se automatiza). La validación **no** va en MySQL.
- **D2 · Rechazo del ficticio** cuando alguien lo escribe. Consecuencia aceptada: al editar un cliente con RUT ficticio hay que corregir el RUT para guardar.
- **D3 · Folio** en `Cotizacion`, distinto del `id` (la clave primaria no cambia). Es lo que se muestra en «Cotización N°». Las existentes reciben `folio = id`.
- **D4 · El «1000» no es lógica del proyecto.** El código asigna el siguiente folio de forma genérica (el proyecto puede partir en 1). El salto a 1000 es una acción única y manual del desarrollador en `python manage.py shell`, documentada como paso del despliegue.
- **D5 · Tabla contador.** La numeración inicial vive como dato. MySQL admite una sola columna `AUTO_INCREMENT` por tabla y ya es el `id`: el folio lo asigna la aplicación.
- **D6 · Destino:** Épica 14, que pasa a «errores y mejoras puntuales» (RDA-024).

## Alcance

### A. RUT del cliente

1. `Cliente.rut = CharField(max_length=12, verbose_name='RUT', validators=[validar_rut])`, obligatorio. **No es `unique`**: todos los existentes comparten el ficticio.
2. Migración `AddField` con `default='00.000.000-0'` y `preserve_default=False`: rellena las filas existentes y deja el campo sin valor por defecto. Los validadores no corren en migraciones.
3. Validador en `pedidos/validadores.py`, declarado en el **modelo** para que lo apliquen formulario, admin y modal de creación rápida: acepta con o sin puntos y guion, `K`/`k`; dígito verificador por módulo 11; rechaza el cuerpo todo en ceros (el ficticio pasa el módulo 11, por eso se rechaza de forma explícita), cuerpos demasiado cortos o con letras.
4. Normalización a `12.345.678-5` (`K` en mayúscula) en un único lugar que cubra los tres caminos; se justifica en la bitácora.
5. JavaScript solo como ayuda visual (formato y aviso) en el formulario de clientes y en el modal; la autoridad es Python. Sin CDN nuevos (`DESIGN.md`).
5b. **(H2, 2026-11-27)** El modal de cliente rápido está escrito a mano en **dos** plantillas, `pedido_form.html:96` y `cotizacion_form.html:95`, e `index.js:216-239` solo envía `nombre`, `telefono` y `email` [código]. Las dos plantillas reciben el campo RUT e `index.js` lo envía y muestra el error que devuelva el servidor; sin esto el modal rechaza todo cliente desde el despliegue. Cambia `index.js`: el despliegue lleva `collectstatic`.
6. El RUT se muestra en el bloque del cliente de `cotizacion_pdf.html` y en el detalle de la cotización solo si ahí ya se muestran teléfono o correo. **Nunca** en `RegistroEvento`, logs ni mensajes.

### B. Folio de cotización

1. Modelo `SecuenciaFolio(nombre único, ultimo_folio PositiveIntegerField)` y `Cotizacion.folio = PositiveIntegerField(unique=True, editable=False)`.
2. Asignación en `Cotizacion.save()` cuando `folio` es nulo, con `transaction.atomic()` propio y `select_for_update` sobre la fila del contador: cubre todos los caminos de creación. Si la transacción de la vista se revierte, el folio no queda consumido (el incremento vive dentro de la misma transacción).
3. Folio de solo lectura~~, también en el admin~~. Las URL siguen usando `pk`. **(H3, 2026-11-27)** `Cotizacion` no está registrada en el admin [código]: queda como AUD-05-031 (Baja, propuesta), fuera de esta iteración.
4. Texto visible con el folio, **sin separador de miles** (`USE_THOUSAND_SEPARATOR = True`, `settings.py:263` ~~`:255`~~; usar `|unlocalize` o formato propio). **(H4)** Con `es-cl` el separador es un espacio: sin el filtro se vería `1 000`, no `1.000` [consola local, 2026-11-27]; `|unlocalize` da `1000`. Los f-strings (nombre del archivo, mensajes) y `{% url %}` no se localizan: PDF, nombre del archivo `Cotizacion_{folio}.pdf`, listado, detalle, título, confirmaciones de eliminar y convertir, y el mensaje del abono por conversión. La búsqueda del listado encuentra por folio.
5. `RegistroEvento.entidad_id` sigue siendo el `pk`; los `resumen` nuevos dicen «folio N».

### C. Respaldos

`verificar_respaldo.py` pasa de 19 a 20 tablas esperadas, con el mismo trato que hoy da a los volcados antiguos de una tabla menos. Se actualizan el script, sus pruebas, `respaldo.md` y `despliegue.md`.

## Clasificación de las migraciones (declarada; se confirma con `sqlmigrate`)

| Migración | Qué hace | Clase declarada |
| :-------- | :------- | :-------------- |
| `0010` | Crea `SecuenciaFolio`; agrega `Cotizacion.folio` **ya obligatorio** con un valor transitorio (`preserve_default=False`, sin `unique`); agrega `Cliente.rut` con relleno del ficticio | **2, aditiva** (tabla nueva y columnas nuevas que nacen `NOT NULL` con relleno en el mismo `ALTER`: no se impone obligatoriedad sobre una columna existente) |
| `0011` | `RunPython`: `folio = id` en las existentes y siembra el contador con el mayor folio (0 si no hay); reversa definida | Datos, sin DDL |
| `0012` | **Solo** el índice único de `folio` | **2, aditiva** (índice) |

~~La `0012` hacía `folio` obligatorio y único sobre una columna creada nula en la `0010`: por la letra de la regla 8.1, Clase 3.~~ **Resuelto el 2026-11-20 (decisión del desarrollador, opción C):** `folio` nace obligatorio con valor transitorio en la `0010`, se rellena en la `0011` y la `0012` agrega solo el índice único. Se confirma con `sqlmigrate` que ningún paso es Clase 3 (en particular, que la `0012` no emite `MODIFY` de la columna); **si alguno lo es, se detiene y se vuelve a preguntar.** La clasificación del RUT también se registra en la bitácora.

Van en tres archivos porque MySQL no revierte DDL a medias: si una falla, las anteriores quedan aplicadas y se sabe exactamente dónde quedó.

## Fuera de alcance

- Columna RUT en la lista de clientes y filtro «RUT por completar» (propuesta en el registro, sección 4).
- Corregir los RUT ficticios (lo hace el dueño, a mano).
- RUT único, búsqueda de clientes por RUT, RUT en pedidos.
- Programar el «1000» en código o migraciones.
- Cambiar las URL de cotizaciones a folio.

## Criterios de aceptación

1. Todo cliente existente tiene `rut = '00.000.000-0'` tras migrar; el formulario de clientes, el admin y el modal rechazan ese valor y los RUT con dígito verificador incorrecto, y guardan los válidos normalizados.
2. El PDF y el detalle de la cotización muestran el RUT del cliente (el detalle, si ya muestra teléfono o correo).
3. Toda cotización existente tiene `folio = id`; el contador queda en el mayor folio.
4. Cada cotización nueva, por cualquier camino, recibe el folio siguiente, sin repetirse, sin reutilizar el de una borrada y sin consumir folio si la transacción se revierte.
5. El folio se ve sin separador de miles en PDF, nombre del archivo, listado, detalle, confirmaciones y mensajes; la búsqueda lo encuentra.
6. Ningún «1000» en código ni migraciones (`grep`).
7. `verificar_respaldo.py` acepta volcados de 20 tablas y trata los de 19 como hoy trata los de 18.
8. Pruebas: ~~411 o más~~ **más de 461** (461 es la cuenta vigente desde la 04-09, más las nuevas de esta iteración), `OK (expected failures=3)`; `check`, `check --deploy` con solo las advertencias conocidas y `makemigrations --check --dry-run` sin cambios.

## Pruebas

- Validador: válidos con y sin formato y con `K`; dígito erróneo; cuerpo en ceros; largo incorrecto; letras.
- Formulario y modal: normalización y rechazo del ficticio.
- Migración de datos: `folio = id`, contador sembrado y reversa.
- Folio: correlativo; sin reutilizar al borrar la última; transacción revertida no consume; todos los caminos asignan; PDF y listado sin separador.
- Verificador de respaldo con 20 tablas.
- RUT de prueba sintéticos: `12.345.678-5` y `11.111.111-1`.

## Despliegue

No se despliega antes de la 04-07 (`v4.9-sanitizacion-html`) y la 04-08. Si la punta de `main` lleva trabajo sin desplegar de otra iteración, se etiqueta un commit anterior (`despliegue.md`, «Etiquetar un commit anterior a la punta»).

1. Respaldo previo **verificado** con `verificar_respaldo.py` (19 tablas antes de migrar).
2. ~~`git pull` en el servidor~~ En el servidor, **solo** `git fetch origin --tags` y `git checkout v14.3-rut-y-folio` (`despliegue.md`, 3.2; nunca `git pull`), **`python manage.py collectstatic --noinput`** (cambia `index.js`, H2) y `python manage.py migrate --plan`: deben aparecer solo `0010`, `0011` y `0012`.
3. `python manage.py migrate`, a una hora de poco uso y con el dueño avisado de no crear clientes ni cotizaciones durante la actualización (aviso 1, opción A).
4. **Paso único del folio**, antes de crear la primera cotización nueva: el bloque de `python manage.py shell` que se escribe y ensaya en la réplica durante la implementación (con `transaction.atomic()` y `select_for_update`; **su guarda mira las cotizaciones existentes con folio ≥ 1000, no el contador**, y se niega si hay alguna; fija `ultimo_folio = 999` e imprime el valor antes y después). Se puede volver a correr (aviso 2, opción C). Tabla de verificación: valor antes, valor después, folio de la primera cotización nueva. Datos de partida: 33 cotizaciones, id 2 a 34, ninguna con id ≥ 1000 [consola, 2026-11-27].
5. Un solo Reload.
6. Respaldo posterior verificado (20 tablas).
5b. Ctrl+F5 en el navegador (carga el `index.js` nuevo).
7. Validación del día 0 (RDA-021): un cliente existente muestra el RUT ficticio y al editarlo se rechaza; una cotización ~~nueva~~ **de prueba** muestra el folio 1000 en pantalla y en el PDF (y en el nombre del archivo). **Aviso 2, opción C:** se borra la cotización de prueba (antes que su cliente de prueba, que está protegido por `PROTECT`), se borra el cliente y se vuelve a correr el paso único (valor antes 1000, después 999), para que la primera cotización real sea la 1000.
8. Retroceso: `retroceso.md`, **con restauración del respaldo previo** (hay migraciones con datos y tabla nueva), y vuelta a `v4.11-csp-observacion` (antes: ~~la etiqueta de la 04-08~~).

Los datos de producción los entrega el desarrollador en `evidencia-14-04.md`.

## Riesgos y avisos

- **Clase de las migraciones:** resuelta (opción C); se confirma con `sqlmigrate`. Entre la `0010` y la `0011` todas las cotizaciones comparten el valor transitorio: por eso el índice único va recién en la `0012`. Si la `0011` fallara, la `0012` no se aplica y la base queda sin índice, no con folios repetidos rechazados a medias.
- **Orden con la 04-08 (decisión del desarrollador, 2026-11-20):** la implementación espera a que la `0009` esté en `main`.
- **Clientes bloqueados al editar:** cualquier edición de un cliente con RUT ficticio exige corregir el RUT (D2, aceptado). Conviene avisar al dueño antes del despliegue.
- **Modal de crear cliente rápido:** desde el despliegue pide RUT; un RUT desconocido en el momento de la venta impide crear el cliente.
- **Disco:** una tabla de una fila y dos columnas cortas; impacto despreciable.
- **Cotizaciones con folio ≥ 1000 existentes:** ~~si ya hay más de 999 cotizaciones~~ el paso único se niega si **`MAX(id)` ≥ 1000** (folio = id), no según el conteo. Medido el 2026-11-27: id 2 a 34, ninguna ≥ 1000 [consola].
- **Ventana entre `migrate` y el Reload (aviso 1, decisión del 2026-11-27: opción A).** Hora de poco uso y aviso al dueño; sin código. Conteo en la parte C de la evidencia (filas 9 a 11). **Plan de contingencia** (escrito, sin código): si aparece un cliente con `rut` vacío, se deja como está (al editarlo el formulario exige un RUT válido) y se anota; si aparece una cotización con `folio = 0`, el desarrollador decide entre asignarle un folio a mano en el shell o restaurar el respaldo previo (parte D); si el índice único rechaza un segundo folio 0 (`IntegrityError` en el conteo de `despliegue.md` 3.12 B, paso 6.3), es un 500 visible: se aplica la regla de retroceso de la parte D.
