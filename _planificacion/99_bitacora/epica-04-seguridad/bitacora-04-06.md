# Bitácora 04-06 · Protección del historial ante borrados en cascada

- **Fecha:** 2026-11-19/20
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** **Completada y verificada en producción (2026-11-20, Reload 10:22:07 hora de Chile)**: `v4.8-historial-clientes` (`8f4e396`), `0008` aplicada. Retroceso vigente `v4.8-historial-clientes` (previo `v4.7-correcciones-config`). Ver «Cierre en producción». ~~Implementada, pendiente de despliegue. Etiqueta prevista `v4.8-historial-clientes`, sin fecha fija (RDA-021); retroceso `v4.7-correcciones-config`. Pendiente del desarrollador: respaldo de la réplica, `SHOW CREATE TABLE` antes y después, `migrate` en la réplica y revisión manual (`despliegue.md`, 3.13 A); después, el despliegue (3.13 B).~~
- **Regla:** solo conteos; ningún nombre, teléfono ni monto de clientes.

## Resumen

AUD-02-001 corregido en código: `Pedido.cliente` y `Cotizacion.cliente` pasan de `CASCADE` a `PROTECT` con la migración `0008_proteger_historial_cliente`, **Clase 1 confirmada** (`sqlmigrate` sin SQL). `eliminar_cliente` rechaza con el mensaje de D1 y sin evento (D3); la confirmación muestra la advertencia de D2 sin ocultar el botón. R14 en verde. Además, el script D2 queda versionado en `scripts/diagnostico/` (excepción a «un despliegue, un propósito», decisión del desarrollador).

## Decisiones del desarrollador (2026-11-19, dichas por él)

- Consulta previa aprobada: crear la `0008` y ejecutar `sqlmigrate` y `migrate` solo en `manzagrafica_replica` con `DB_NAME` en la sesión; antes de `migrate`, confirmar el respaldo de la réplica. `SHOW CREATE TABLE` los ejecuta él. Conteos con un script ORM fuera del repo.
- Retroceso: caso 1 a `v4.7` y Reload; `migrate pedidos 0007` opcional, solo si estorba. `retroceso.md` aclara que el caso 2 rige también para Clase 1.
- Script D2 versionado con docstring, pruebas con volcados ficticios y mención en `despliegue.md`; excepción a RDA-007.
- `migrate` después del checkout y antes del Reload (3.4).
- **2026-11-20, respuesta a la pregunta del agente:** el respaldo de la réplica **aún no** está; **no migrar**. `migrate` queda para el desarrollador.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/models.py` (CRLF) | `:37` y `:164`: `PROTECT`. |
| `pedidos/migrations/0008_proteger_historial_cliente.py` | Nueva, generada por `makemigrations` (dos `AlterField`, depende de `0007_registroevento`). |
| `pedidos/views.py` (LF) | `eliminar_cliente`: `try`/`except ProtectedError`/`else`, fuera de cualquier bloque atómico. |
| `pedidos/templates/pedidos/cliente_confirm_delete.html` (CRLF) | Recuadro de error (`role="alert"`, sin `animate-pulse`) y advertencia de D2. |
| `pedidos/tests/test_regresiones.py` (CRLF) | R14 sin `@expectedFailure` ni `@tag('regresion')`; docstring actualizado. |
| `pedidos/tests/test_historial_clientes.py` | Nueva: 4 pruebas (solo cotización; vista con y sin historial; GET). |
| `pedidos/tests/test_script_d2.py` | Nueva: 5 pruebas del script con volcados ficticios. |
| `scripts/diagnostico/revisar_volcado_d2.py` | Nuevo (copia del script de la 04-05 con ruta propia y `main(argv)`). |
| `docs/operacion/despliegue.md` (CRLF) | Sección 3.13 (réplica, migración, orden) y fila prevista en la sección 5. |
| `docs/operacion/retroceso.md` | Caso 2 rige también para Clase 1. |
| `docs/operacion/pruebas.md` (CRLF) | Valor vigente `expected failures=3` (estaba en 9 desde antes de la 04-01) y R14 retirada. |
| Iteración, `definicion-epica-04.md`, `auditoria-tecnica.md`, `registro-pendientes.md` (CRLF), esta bitácora | Estado y correcciones. |

**Fuera del repo:** `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\5aabf0ec-527a-461d-bf18-73b4fa81c16a\scratchpad\conteos_04_06.py` (conteos por ORM, solo números).

## Correcciones a la redacción

- Líneas al 2026-11-19: `eliminar_cliente` en `views.py:739-746` (no `:690-697`; borra en `:743`); `eliminar_producto` en `:1172-1189`; `eliminar_pedido` en `:386`; R14 en `test_regresiones.py:375`; `test_eventos_negocio.py:121`. Las de `models.py` seguían exactas.
- La 04-01 no cambió `eliminar_cliente` (comprobación explícita del método, sin `require_POST`).
- Pregunta de pagos en cascada: respondida el 2026-11-18 (intencional); textos tachados.
- Plan de retroceso reemplazado por el del desarrollador.
- La URL del admin es `/acceso-manzagrafica-admin/`, no `/admin/`.

## `sqlmigrate pedidos 0008` (réplica, `DB_NAME=manzagrafica_replica`)

```text
--
-- Alter field cliente on cotizacion
--
-- (no-op)
--
-- Alter field cliente on pedido
--
-- (no-op)
```

Sin `ALTER`, `DROP` ni `ADD CONSTRAINT`: **Clase 1**. `migrate pedidos --plan` en la réplica: solo `pedidos.0008_proteger_historial_cliente` (dos `Alter field`).

## Verificación: antes y después

| Comprobación | Antes | Después |
| :----------- | :---- | :------ |
| `test pedidos` | 379, `OK (expected failures=4)` (R8, R9, R14, R15) | 388, `OK (expected failures=3)` (R8, R9, R15) |
| Pruebas nuevas antes del cambio | — | 4 fallos: R14 y 3 de `test_historial_clientes` (la de «sin historial» ya pasaba, como corresponde) |
| `check` | Sin problemas | Sin problemas |
| `makemigrations --check --dry-run` | `No changes detected` | `No changes detected` (con la `0008` creada) |
| `showmigrations pedidos`, réplica | Hasta `0007` `[X]` | `0008` `[ ]`: **no aplicada** (decisión del desarrollador) |
| Conteos, réplica | clientes 825, pedidos 992, ítems de pedido 999, pagos 1198, cotizaciones 33, ítems de cotización 65; clientes con historial 793, sin historial 32 | Tras el `migrate` del desarrollador (visto en consola): 824, 992, 999, 1198, 33 y 65; clientes bajó por el borrado accidental, el resto igual |
| `SHOW CREATE TABLE` | SHA-256 `0830026E…7E3F`, 2324 bytes, 2 `CREATE TABLE` (consola) | Mismo SHA-256 y 2324 bytes (consola): **Clase 1 confirmada en MySQL** |
| `migrate`, réplica | — | OK y `[X] 0008` (consola, desarrollador) |
| Revisión manual (escritorio y 360 px) | — | Pruebas A a D correctas y evento `cliente_eliminado` registrado (dicho por el desarrollador) |

Nota: la base local por defecto (sin `DB_NAME`) muestra `0007` sin aplicar; no se tocó. Todo se hizo sobre la réplica.

## Riesgos y lo que no se vio

- ~~`migrate` no se ensayó en la réplica: la Clase 1 descansa en `sqlmigrate` hasta que el desarrollador compare `SHOW CREATE TABLE`.~~ Superado el 2026-11-20: el desarrollador migró la réplica y el hash de `SHOW CREATE TABLE` no cambió (ver «Cierre en producción»).
- Un cliente con historial ya no se puede borrar ni archivar (efecto buscado; archivar sería funcionalidad nueva).
- El admin cambia su comportamiento al borrar clientes (inferido de Django; se revisa en 3.13 A).
- `mysql.W002` (modo estricto) aparece en `migrate --plan`: conocido, AUD-02-020, Épica 06.
- No se vio: el navegador, el `.env`, los respaldos y el servidor.
- D5 de la 04-03 sigue `PENDIENTE_DESARROLLADOR`.

## Cierre en producción (2026-11-20, hora de Chile; cierre documental, solo documentos)

**Verificado en consola (salidas pegadas por el desarrollador):**

- Respaldo previo `respaldo_20-11-2026_10-16-37.sql`: 1.549.877 bytes, 19 de 19 tablas, `CUMPLE D2`, SHA-256 `524C32FC27EFD0ECF451E342941BA0B34D2EAA6470E555ED4B14D51123AB09FE`.
- Etiqueta anotada `v4.8-historial-clientes` sobre `8f4e396`, publicada.
- Servidor: `migrate --plan` solo `0008`; `check --deploy` solo W005 y W021; `migrate` OK, `[X] 0008`.
- **Un solo Reload:** `Starting uWSGI` 10:22:07, único hasta las 10:54. Conteo de `Traceback`, `OperationalError`, «gone away» y `TemplateDoesNotExist` desde el arranque: **0**, a las 10:27, **antes** del uso en navegador.

**Dicho por el desarrollador (no visto):** panel y `/clientes/lista/` sin 500; la confirmación de eliminar un cliente con pedidos muestra la advertencia; no se pulsó eliminar. **No hay conteo de errores posterior al uso.**

**Réplica:** durante la revisión se borró por accidente un cliente sin historial (825 → 824 clientes; sin nombre). No afecta producción. **Revisión manual de 3.13 A, cumplida** (corrección del 2026-11-20): visto en consola, `sqlmigrate` `(no-op)` en las dos operaciones, `migrate` OK y `[X] 0008`, SHA-256 de `SHOW CREATE TABLE` igual antes y después (`0830026E…7E3F`, 2324 y 2324 bytes, 2 `CREATE TABLE`) y conteos 824, 992, 999, 1198, 33 y 65; dicho por el desarrollador, pruebas A a D en escritorio y a 360 px correctas y el evento `cliente_eliminado` registrado.

**Respaldo antes del checkout (corrección del 2026-11-20, visto en consola):** `error.log` registra la rotación de respaldos a las 10:16:41 (13:16:41 UTC); a las 10:20 `git describe --tags` decía `v4.7-correcciones-config`; el checkout a `v4.8` fue a las 10:21. El respaldo se tomó con `v4.7` activo, como exige 3.13 B, paso 1.

**AUD-05-023 (decisión del desarrollador, 2026-11-20):** Épica 14, tema Clientes, dentro del arreglo mínimo; la lista mostrará también las cotizaciones.

**Auditoría:** AUD-02-001 pasa a «Resuelto · verificado en producción (2026-11-20)».

**Correcciones a `despliegue.md`:** 3.13 A, paso 5, citaba un «script de conteos» que no existe en el repositorio: ahora usa `SELECT COUNT(*)` por tabla. 3.13 B, paso 6: advierte que `DESDE_CL` lleva la fecha real y que sin «`DESDE_CL válido`» la consulta no sirve.

**Hallazgos de la lista de clientes y sus destinos:** registrados en `auditoria-tecnica.md` (AUD-05-021 a AUD-05-024) y en RDA-023 (`decisiones.md`), decididos por el desarrollador el 2026-11-20.

**Siguen abiertos:** D5 de la 04-03 (`PENDIENTE_DESARROLLADOR`), AUD-01-016 punto 3 (observación tras una hibernación) y renovar la web app antes del 2026-12-13.
