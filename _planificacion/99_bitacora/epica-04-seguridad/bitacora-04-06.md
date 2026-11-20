# Bitácora 04-06 · Protección del historial ante borrados en cascada

- **Fecha:** 2026-11-19/20
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Implementada, pendiente de despliegue. Etiqueta prevista `v4.8-historial-clientes`, sin fecha fija (RDA-021); retroceso `v4.7-correcciones-config`. **Pendiente del desarrollador:** respaldo de la réplica, `SHOW CREATE TABLE` antes y después, `migrate` en la réplica y revisión manual (`despliegue.md`, 3.13 A); después, el despliegue (3.13 B).
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
| Conteos, réplica | clientes 825, pedidos 992, ítems de pedido 999, pagos 1198, cotizaciones 33, ítems de cotización 65; clientes con historial 793, sin historial 32 | Pendiente: tras el `migrate` del desarrollador (deben ser iguales) |
| `SHOW CREATE TABLE` | Pendiente (desarrollador, 3.13 A paso 3) | Pendiente (paso 5; mismo hash) |
| Revisión manual (escritorio y 360 px) | — | Pendiente (desarrollador, 3.13 A pasos 7 y 8) |

Nota: la base local por defecto (sin `DB_NAME`) muestra `0007` sin aplicar; no se tocó. Todo se hizo sobre la réplica.

## Riesgos y lo que no se vio

- `migrate` no se ensayó en la réplica: la Clase 1 descansa en `sqlmigrate` hasta que el desarrollador compare `SHOW CREATE TABLE`.
- Un cliente con historial ya no se puede borrar ni archivar (efecto buscado; archivar sería funcionalidad nueva).
- El admin cambia su comportamiento al borrar clientes (inferido de Django; se revisa en 3.13 A).
- `mysql.W002` (modo estricto) aparece en `migrate --plan`: conocido, AUD-02-020, Épica 06.
- No se vio: el navegador, el `.env`, los respaldos y el servidor.
- D5 de la 04-03 sigue `PENDIENTE_DESARROLLADOR`.
