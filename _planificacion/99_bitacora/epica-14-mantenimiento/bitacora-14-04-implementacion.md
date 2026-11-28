# Bitácora 14-04 · Implementación (RUT del cliente y folio de cotización)

- **Fecha:** 2026-11-27
- **Estado de la iteración:** En revisión. Implementada en local; faltan el ensayo en la réplica, la revisión manual (escritorio y 360 px) y el despliegue, que hace el desarrollador (evidencia, partes A a E).
- **Commit base:** `main` con la parte documental del análisis ya confirmada. Sin commit, etiqueta ni despliegue. Nada contra la réplica ni producción: las pruebas usan la base `test_…`.
- **Rótulos:** **[doc]** documento; **[código]** leído o escrito en el código; **[prueba]** salió de una prueba o comando local; **[inferido]** conclusión no comprobada.

## Verificación previa

| Punto | Resultado |
| :---- | :-------- |
| Suite antes de empezar | `Ran 461 tests`, `OK (expected failures=3)`, 963 s [prueba]. **Salvedad:** mientras corría se editaron plantillas y vistas; los módulos ya estaban cargados, pero no es una medición limpia del estado de partida |
| Última migración | `0009_acceso_bloqueado` [código] |
| Decisiones | Las del 2026-11-27 de [bitacora-14-04-analisis](bitacora-14-04-analisis.md) [doc] |

## Qué se hizo

### A. RUT

- `pedidos/validadores.py` (nuevo): `validar_rut`, `normalizar_rut`, `digito_verificador`, `RUT_PROVISORIO`. Acepta cuerpo de 7 u 8 dígitos, con puntos bien puestos o sin ninguno, guion opcional, `k`/`K`; módulo 11; códigos de error `rut_formato`, `rut_provisorio` (cuerpo en ceros, aunque pase el módulo 11) y `rut_digito`. Los mensajes no repiten el valor escrito (dato personal) [código].
- `Cliente.rut = CharField(max_length=12, verbose_name='RUT', validators=[validar_rut])`, obligatorio, **sin `unique`** [código].
- **Normalización en un solo lugar: `Cliente.clean()`.** El formulario de clientes, el admin y el modal rápido usan un `ModelForm`, que llama a `full_clean()`: primero corren los validadores sobre lo escrito y después `clean()` deja el valor como `12.345.678-5`. Se eligió `clean()` y no `save()` porque así un valor inválido nunca llega a normalizarse y porque es el punto común de los tres caminos sin tocar las vistas [código, prueba]. Límite: `Cliente.objects.create()` no pasa por `clean()` (solo lo usan las pruebas; la factoría ya trae un RUT normalizado) [código].
- Admin de clientes: sin cambios en `admin.py`; hereda el validador y la normalización (prueba `test_admin_normaliza_y_rechaza`) [prueba].
- Modal rápido (H2): campo `new_client_rut` en `pedido_form.html` y `cotizacion_form.html`, con `label for`, `maxlength="12"` y sin estilos ni scripts en línea. `index.js` lo envía, exige los tres obligatorios antes de enviar (solo ayuda) y muestra los mensajes de error del servidor en texto, en vez del JSON crudo [código].
- RUT visible en el detalle (que ya muestra teléfono y correo) y en el PDF (fila nueva bajo «Cliente») [código, prueba]. No aparece en `RegistroEvento`, registros ni mensajes [código].

### B. Folio

- `SecuenciaFolio(nombre único, ultimo_folio)` y `Cotizacion.folio = PositiveIntegerField(unique=True, editable=False)` [código]. Retención: una fila por numeración, sin crecimiento; no necesita purga (`AGENTS.md` 8.11).
- `Cotizacion.save()`: si `folio` es `None`, abre un `transaction.atomic()` propio, toma la fila del contador con `select_for_update`, suma 1 e inserta. Si la vista se revierte, el incremento también. Si el guardado falla, la instancia queda con `folio = None` (con `try/finally`, sin capturar la excepción; regla 8.4) [código, prueba].
- Si la fila del contador no existe, parte del mayor folio ya usado [código, prueba].
- Caminos [código, prueba]: crear (`views.py`, `crear_cotizacion`) asigna; editar y convertir conservan el folio. Nota del abono: `Abono inicial por conversión de la cotización folio N`; resumen del evento: `Cotización folio N convertida en el pedido #M` (el `entidad_id` sigue siendo el `pk`); PDF `Cotizacion_{folio}.pdf`; búsqueda del listado por folio exacto, con o sin `#`.
- Plantillas: `{{ …folio|unlocalize }}` en las seis de cotizaciones (título, número, listado, confirmaciones y PDF). Las URL siguen con `pk` [código, prueba: `1234` sin `1 234` ni `1.234`].
- **Paso único** (`pedidos/paso_unico_folio.py`, nuevo): `fijar_inicio_folio(inicio)` es genérica (el número lo escribe el desarrollador en la consola, D4), bloquea el contador, **se niega si alguna cotización tiene folio ≥ inicio** (mira las cotizaciones, no el contador), fija `inicio - 1` y devuelve `(hecho, texto)` con antes y después. No usa `print` (regla 8.8): el bloque de consola lo imprime. Ensayada solo en la base de prueba [prueba].

### C. Respaldos

`verificar_respaldo.py` pasa a 20 tablas (`pedidos_secuenciafolio`); los volcados de 19 se verifican con la versión de `v4.11`, igual que los de 18 con la de `v0.2` [código, doc]. Prueba nueva `test_verificar_respaldo.py` (no había pruebas del script) [prueba]. `respaldo.md` y `despliegue.md` (sección 3.17 nueva) al día [doc].

## Migraciones (creadas a mano, con permiso del desarrollador, 2026-11-27)

`makemigrations` las habría juntado en una sola con `unique`; se escribieron a mano para respetar la opción C. `makemigrations --check --dry-run`: `No changes detected` [prueba].

```sql
-- 0010_rut_y_folio (Clase 2, aditiva)
CREATE TABLE `pedidos_secuenciafolio` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `nombre` varchar(30) NOT NULL UNIQUE, `ultimo_folio` integer UNSIGNED NOT NULL CHECK (`ultimo_folio` >= 0));
ALTER TABLE `pedidos_cotizacion` ADD COLUMN `folio` integer UNSIGNED DEFAULT 0 NOT NULL CHECK (`folio` >= 0);
ALTER TABLE `pedidos_cotizacion` ALTER COLUMN `folio` DROP DEFAULT;
ALTER TABLE `pedidos_cliente` ADD COLUMN `rut` varchar(12) DEFAULT '00.000.000-0' NOT NULL;
ALTER TABLE `pedidos_cliente` ALTER COLUMN `rut` DROP DEFAULT;

-- 0011_folio_igual_id (datos, sin DDL)
-- Raw Python operation
-- THIS OPERATION CANNOT BE WRITTEN AS SQL

-- 0012_folio_unico (Clase 2, solo índice)
ALTER TABLE `pedidos_cotizacion` ADD CONSTRAINT `pedidos_cotizacion_folio_36c672ad_uniq` UNIQUE (`folio`);
```

- **Clasificación [prueba]:** la `0010` crea una tabla y agrega columnas nuevas que nacen `NOT NULL` con relleno en el mismo `ALTER`; los `DROP DEFAULT` solo quitan el valor por defecto de columnas recién creadas. La `0012` **no trae `MODIFY`**. Ninguna es Clase 3.
- **`0011`:** `UPDATE … SET folio = id` en una sola sentencia y el contador con el mayor folio (0 si no hay). Reversa: `folio = 0` y borra la fila del contador [código]. La reversa en la réplica se ensaya en A2.8.
- **Aviso 1 [inferido, sin cambios]:** tras el `DROP DEFAULT`, un `INSERT` del código viejo sin modo estricto guarda `0` y `''`; se cubre con la opción A decidida.
- No se corrió `migrate` en `manzagrafica_local` ni en la réplica; solo la base `test_…` las aplicó.

## Pruebas

- **Nuevas:** `test_rut_folio.py` (35) y `test_verificar_respaldo.py` (4), 39 en total, en verde [prueba]. Cubren el validador, la normalización por formulario, vista, modal y admin, el RUT compartido, el folio (correlativo, sin reutilizar, transacción revertida, fallo al guardar, sin fila del contador, 4 hilos concurrentes con folios distintos), todos los caminos, los textos sin separador, el detalle y el PDF con RUT, el nombre del PDF, la búsqueda y el paso único (hecho, negado y vuelto a correr tras borrar).
- **Orden:** las pruebas se escribieron antes del código, pero **no se ejecutaron en rojo** antes de implementar (la base de prueba estaba ocupada por la suite base). Contra `HEAD` fallan al importar `pedidos.validadores` y `SecuenciaFolio` [inferido].
- **Ajustadas por contrato nuevo:** `test_cotizaciones.py` (nota del abono con folio), `test_eventos_negocio.py` (resumen con folio), `test_acceso.py` (el cliente rápido lleva un RUT sintético), `factorias.py` (RUT sintético `12.345.678-5`).
- **Suite completa:** `Ran 500 tests in 1064.461s`, `OK (expected failures=3)` (461 + 39) [prueba]. `makemigrations --check --dry-run`: `No changes detected` [prueba].
- `check`: `System check identified no issues (0 silenced)` [prueba].
- `grep` de «1000» en el código y las migraciones de la iteración: ninguno; las únicas coincidencias en `views.py` (`:635`, `:1501`) son el ancho de los gráficos SVG, anteriores y ajenas al folio [prueba].
- RUT usados: solo los sintéticos `12.345.678-5`, `11.111.111-1` y `1.000.005-K` (este último para probar la `K`).

## Desviaciones y decisiones propias

| # | Qué | Por qué |
| :- | :-- | :------ |
| 1 | El paso único vive en un módulo (`pedidos/paso_unico_folio.py`) y la consola solo lo llama | Probarlo (hecho, negado, vuelto a correr) en vez de pegar un bloque largo sin probar en la consola de PythonAnywhere. El número sigue fuera del código (D4). Si prefieres un bloque autocontenido, se puede volver atrás |
| 2 | `index.js` muestra los errores del servidor como texto | Con el RUT, el error más común en el modal viene del servidor; el JSON crudo no se lee bien |
| 3 | `__str__` de la cotización usa el folio | Coherencia con lo visible |
| 4 | No se tocó `admin.py` | El admin de clientes hereda todo del modelo (H3: sin admin de cotizaciones) |

## Pendiente para el desarrollador

- Ensayo en la réplica (A2), revisión manual a 360 px (A2b), avisos (A0) y despliegue (`despliegue.md` 3.17; evidencia B a E).
- Respaldo previo (A3) verificado con la versión de `v4.11` del script (dato 4).
- **Requiere respaldo previo al despliegue:** sí, obligatorio (migraciones con datos y tabla nueva).
